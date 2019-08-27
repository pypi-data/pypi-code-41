from typing import Optional, Any, Dict, List

from aurora_connector.helpers.Utils import format_response, format_sql_parameters
from aurora_connector.helpers.Exceptions import AuroraDatabaseException

import boto3
RDS_CLIENT = boto3.client("rds-data")


class AuroraDatabase:

    def __init__(self, database_name: str, db_cluster_arn: str, db_credentials_secrets_store_arn: str) -> None:
        """
        Creates a programmatic interface for an AWS Aurora Serverless cluster

        :param database_name: The name of the database. Relates to AWS::RDS::Cluster property DatabaseName. (string)
        :param db_cluster_arn: The RDS cluster amazon resource name. (string)
        :param db_credentials_secrets_store_arn: The amazon resource name for the AWS::SecretsManager::Secret credentials store. (string)
        """

        self._database_name = database_name
        self._db_cluster_arn = db_cluster_arn
        self._db_credentials_secrets_store_arn = db_credentials_secrets_store_arn

        self._transaction_id = None

    @property
    def database_name(self) -> str:
        """
        Returns the name of the database.

        :return: (string)
        """
        return self._database_name

    @property
    def db_cluster_arn(self) -> str:
        """
        Returns the RDS cluster amazon resource name.

        :return: (string)
        """
        return self._db_cluster_arn

    @property
    def db_credentials_secrets_store_arn(self) -> str:
        """
        Returns the database secrets store amazon resource name.

        :return: (string)
        """
        return self._db_credentials_secrets_store_arn

    @property
    def transaction_id(self) -> Optional[str]:
        """
        Returns the transaction_id. If the database is not "in" a transaction then None is returned, otherwise
        a string containing the UUID for the transaction_id is returned

        :return: (string|None)
        """
        return self._transaction_id

    def _in_transaction(self) -> bool:
        """
        Returns whether the database is currently in a transaction.
        We define the database being "in" a transaction if and only if
        a transaction has been started but not committed or rolled back

        :return: (boolean)
        """

        return self._transaction_id is not None

    def _begin_transaction(self) -> None:
        """
        Begins an AWS Aurora Serverless transaction.
        If a transaction is successfully started then the AuroraDatabase property :property transaction_id:
        is assigned the transactionId returned from the Data API.

        Note that we cannot begin a new transaction while currently "in" a transaction.
        An AuroraDatabaseException is thrown if this occurs.

        :return: (None)
        """

        if self._in_transaction():
            raise AuroraDatabaseException({
                "message": "Cannot start a new transaction while currently being in a transaction.",
                "transaction_id": self.transaction_id
            })

        try:
            response = RDS_CLIENT.begin_transaction(
                database=self.database_name,
                resourceArn=self.db_cluster_arn,
                secretArn=self.db_credentials_secrets_store_arn
            )
            self._transaction_id = response.get("transactionId")
        except Exception as error:
            raise AuroraDatabaseException(error) from error

    def commit(self) -> None:
        """
        Commits an AWS Aurora Serverless transaction.
        If the transaction is successfully committed then the AuroraDatabase property :property transaction_id:
        is assigned None.

        Note that we cannot commit a transaction if we're not currently "in" a transaction.
        An AuroraDatabaseException is thrown if this occurs.

        :return: (None)
        """

        if not self._in_transaction():
            return
            # raise AuroraDatabaseException({
            #     "message": "Cannot commit a transaction if a transaction hasn't been initiated.",
            #     "transaction_id": self.transaction_id
            # })

        try:
            RDS_CLIENT.commit_transaction(
                resourceArn=self.db_cluster_arn,
                secretArn=self.db_credentials_secrets_store_arn,
                transactionId=self.transaction_id
            )

            # Reset transaction_id
            self._transaction_id = None
        except Exception as error:

            # Panic. If error occurs while committing transaction then reset transaction_id and then raise exception
            self._transaction_id = None
            raise AuroraDatabaseException(error) from error

    def rollback(self) -> None:
        """
        Rolls back an AWS Aurora Serverless transaction.
        If the transaction is successfully rolled back then the AuroraDatabase property :property transaction_id:
        is assigned None.

        Note that we cannot rollback a transaction if we're not currently "in" a transaction.
        An AuroraDatabaseException is thrown if this occurs.

        :return: (None)
        """

        if not self._in_transaction():
            raise AuroraDatabaseException({
                "message": "Cannot rollback a transaction if a transaction hasn't been initiated.",
                "transaction_id": self.transaction_id
            })

        try:
            RDS_CLIENT.rollback_transaction(
                resourceArn=self.db_cluster_arn,
                secretArn=self.db_credentials_secrets_store_arn,
                transactionId=self.transaction_id
            )

            # Reset transaction_id
            self._transaction_id = None
        except Exception as error:

            # Panic. If error occurs while committing transaction then reset transaction_id and then raise exception
            self._transaction_id = None
            raise AuroraDatabaseException(error) from error

    def _execute_statement(self, sql: str, sql_parameters: Dict[str, Any]) -> None:
        """
        Executes SQL statement.
        This method is only for statements that should use transaction in order to maintain ACID.
        If we're not "in" a transaction then begin a new transaction and then execute the statement.

        :param sql: the SQL statement to run (string)
        :param sql_parameters: A dictionary of parameters in the format: {parameter_name, parameter_value, } (dict)
        :return: (None)
        """

        if not self._in_transaction():
            self._begin_transaction()

        try:
            RDS_CLIENT.execute_statement(
                database=self.database_name,
                resourceArn=self.db_cluster_arn,
                secretArn=self.db_credentials_secrets_store_arn,
                transactionId=self.transaction_id,
                sql=sql,
                parameters=format_sql_parameters(sql_parameters)
            )
        except Exception as error:
            raise AuroraDatabaseException(error) from error

    def query(self, sql: str, sql_parameters: Dict[str, Any] = {}) -> List[List]:
        """
        Queries the AWS Aurora Serverless cluster and returns the result set with the following format:
            result_set = [
                [column_1, column_2, ..., column_n],
                .
                .
                .
            ]

        :param sql: the SQL statement to run (string)
        :param sql_parameters: A dictionary of parameters in the format: {parameter_name, parameter_value, } (dict)
        :return: (list)
        """

        try:
            response = RDS_CLIENT.execute_statement(
                includeResultMetadata=True,
                database=self._database_name,
                resourceArn=self._db_cluster_arn,
                secretArn=self._db_credentials_secrets_store_arn,
                sql=sql,
                parameters=format_sql_parameters(sql_parameters)
            )

            return format_response(response)
        except Exception as error:
            raise AuroraDatabaseException(error) from error

    def insert(self, sql: str, sql_parameters: Dict[str, Any] = {}) -> None:
        """
        A wrapper for AuroraDatabase.execute. To be used when executing an INSERT INTO statement.

        :param sql: the SQL statement to run (string)
        :param sql_parameters: A dictionary of parameters in the format: {parameter_name, parameter_value, } (dict)
        :return: (None)
        """

        self.execute(sql, sql_parameters)

    def delete(self, sql: str, sql_parameters: Dict[str, Any] = {}) -> None:
        """
        A wrapper for AuroraDatabase.execute. To be used when executing an DELETE FROM statement.

        :param sql: the SQL statement to run (string)
        :param sql_parameters: A dictionary of parameters in the format: {parameter_name, parameter_value, } (dict)
        :return: (None)
        """

        self.execute(sql, sql_parameters)

    def update(self, sql: str, sql_parameters: Dict[str, Any] = {}) -> None:
        """
        A wrapper for AuroraDatabase.execute. To be used when executing an UPDATE statement.

        :param sql: the SQL statement to run (string)
        :param sql_parameters: A dictionary of parameters in the format: {parameter_name, parameter_value, } (dict)
        :return: (None)
        """

        self.execute(sql, sql_parameters)

    def execute(self, sql: str, sql_parameters: Dict[str, Any] = {}) -> None:
        """
        A public wrapper for AuroraDatabase._execute_statement. To be used when executing any statement that required ACID.

        :param sql: the SQL statement to run (string)
        :param sql_parameters: A dictionary of parameters in the format: {parameter_name, parameter_value, } (dict)
        :return: (None)
        """

        try:
            self._execute_statement(sql, sql_parameters)
        except Exception as error:
            raise AuroraDatabaseException(error) from error
