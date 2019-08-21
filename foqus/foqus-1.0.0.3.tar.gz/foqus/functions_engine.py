#! /usr/bin/python
# -*- coding:utf-8 -*-
from foqus.customers import *
from foqus.request_api import *
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import string, random, hashlib, uuid, tldextract

api = APIFoqus()


def customer_inscription(customer_email, customer_name, customer_type, type_user):
    api_key = str(uuid.uuid4())
    token = str(uuid.uuid4())
    password = ''.join(random.choice(string.ascii_uppercase) for _ in range(8))
    logger.info('Password for client %s is %s' % (customer_email, password))
    hash_password = hashlib.sha512(password.encode('utf-8')).hexdigest()

    add_customer = db.add_customer(customer=customer_name, customerPassword=hash_password, customerEmail=customer_email,
                                   customerJob="", customerPhone="", token=token, aboutUs="", subjectHelp="",
                                   domaine=customer_type, firstName="", lastName="", stafNumber="", apikey=api_key,
                                   expiration_duration_in_hours=100, type=type_user)


    if add_customer:
        db.commit_db_changes()
        # sending email
        customer = db.get_profile(table_name=DATABASE_USERS_MANAGEMENT_TABLE_NAME,
                                  customerEmail=customer_email)
        full_url = DOMAIN + 'activate/' + urlsafe_base64_encode(force_bytes(customer[0])).decode('utf-8')\
                + '/' + customer[12]
        send_inscription_email(customer_email, full_url, password)
        send_inscription_email(customer_email, full_url, password)
        return api_key
    else:
        return 'The email address is already in use. Please try another email address.'


def start_training(customer_name=None, customer_type=None, customer_universe=None):
    response = api.apipost('', customer_name, customer_type, None, None,
                           customer_universe)


def list_all_clients_with_projects():
    result = []
    response = db.select_list_all_clients_with_projects("status_projects")
    try:
        df = DataFrame(response.groupby(['customer_name', 'customer_type']))
        for i in range(0, len(df)):
            customer_nametype = str(df[0][i])
            values = df[1][i]
            list_index = list(values.index)
            name = {'customer_name': customer_nametype.split("', '")[0].replace("('", "")}
            type = {'customer_type': customer_nametype.split("', '")[1].replace("')", "")}
            response = []
            for j in list_index:
                response.append({'project': values['project'][j], 'api': values['api'][j], 'status': values['status'][j],
                                 'name': values['name'][j]})

            projects = {'projects': response}
            data = [name, type, projects]
            result.append(data)
    except Exception as e:
        logger.error("Error in getting user with projects %s" %e)
    return result


def customer_authentication_api(customerEmail, customerPassword, type_user):
    is_authenticated = db.login(customerEmail=customerEmail, customerPassword=customerPassword, type_user=type_user)
    return is_authenticated


def number_post_per_clients():
    response = db.select_number_post_per_clients("client_history_table")
    result = []
    for res in response:
        name = {'customer_name': res[1]}
        type = {'customer_type': res[2]}
        nb_post = {'number_post': res[0]}
        data = [name, type, nb_post]
        result.append(data)
    return result


def predict_image(image_path, customer_name, customer_type, project_name, similars=None):
    response = api.apiget('get_category', customer_name, customer_type, project_name, image_path)
    today = datetime.date.today().strftime("%Y-%m-%d")
    category = json.loads(response)
    image_domaine = (tldextract.extract(image_path)).domain
    if similars is None:

        db.insert_or_update_into_table_history('client_history_table', today, customer_name, customer_type,
                                               project_name, image_path, 'classification', json.dumps({}),
                                               response, ip_adress="",domain_url=image_domaine , type_reference="")

    return category


def get_historic(customer_name, customer_type):
    response_historic = []
    list_response = db.select_similars_classification_result("client_history_table",  customer_name, customer_type)
    for response in list_response:
        each_search = []
        each_search.append({"date": response[1].strftime("%d-%m-%Y")})
        each_search.append({"project": response[4]})
        each_search.append({"url": response[5]})
        each_search.append({"api": response[6]})
        each_search.append(json.loads(response[7]))
        each_search.append(json.loads(response[8]))
        each_search.append({"country": response[11]})
        each_search.append({"searched_time": response[9]})
        response_historic.append(each_search)

    return {"response": response_historic}


def get_client_payment_status(customer_name , customer_type):
    response = db.get_client_payment(customer_name, customer_type)
    return response


def get_apikey_expiration(customer_name):
    # TODO add customer_type to the function
    apikey = db.get_apikey_from_customer(customer_name)[0]
    response = datetime.datetime.fromtimestamp(get_apikey_expiration(apikey)).strftime(
                    " Le %d-%m-%Y  à %I:%M:%S")
    return response


def get_client_statistics(customer_name,customer_type ):
    response1 = get_counter_of_last_four_months(customer_name, customer_type)
    response2 = db.get_sum_of_counter_from_country_code('client_history_table', customer_name, customer_type)
    response3 = db.get_date_and_counter_from_historic_table('client_history_table', customer_name, customer_type , month=str(datetime.date.today())[5:7])
    response4 = scores_repartition_per_users(customer_name, customer_type)
    requests_four_last_months = {}
    for i in range(0, len(response1)):
        requests_four_last_months[response1[i][0]]= (response1[i][1])
    request_by_country = {}
    for c in range(0,len(response2)):
        request_by_country[response2[c][1]] = response2[c][0]
    score_repartition_per_user = {}
    score_repartition_per_user["[10%-30%]"] = response4[0]
    score_repartition_per_user["[30%-50%]"] = response4[1]
    score_repartition_per_user["[50%-75%]"] = response4[2]
    score_repartition_per_user["[75%-90%]"] = response4[3]
    score_repartition_per_user["[90%-100%]"] = response4[4]
    daily_request_current_month= {}
    for j in range(0, len(response3)):
        daily_request_current_month[(response3[j][1]).strftime('%d-%m-%Y')] = (response3[j][0])
    result = {
                'number_of_requests_for_the_four_last_months': requests_four_last_months,
                'request_repartition':request_by_country,
                'daily_request_for_current_month':daily_request_current_month,
                'scores_repartition_per_users':score_repartition_per_user,
            }
    return result


def get_details_trainings_for_client(customer_name,customer_type,project_name, api ):
    response = db.get_training_detalis('status_projects',customer_name, customer_type, project_name, api)
    status_training = response[2]
    if response[1] == 0:
        date_end_training = ""
        url_training_file = ""
    else:
        info_last_training = json.loads(response[0])['training'+ str(response[1])]
        date_end_training = info_last_training['date_end_training']
        url_training_file = info_last_training['url_training_file']

    result={'url_training_file': url_training_file,
            'date_end_training': date_end_training,
            'status_training': status_training}
    return result


def get_details_trainings_for_admin(customer_name,customer_type,project_name, api ):
    response = db.get_training_detalis('status_projects', customer_name, customer_type, project_name, api)
    if response is not None:
        result={'trainings_details':json.loads(response[0]),
                'number_trainings_by_project': response[1],
                'status_last_training': response[2]}
    else:
        result = {'trainings_details': '',
                  'number_trainings_by_project': 0,
                  'status_last_training': 0}
    return result




def historic_users_management():
    response = db.get__historic_users_management()
    result = []
    for res in response:
        email = {'email': res[0]}
        customer_name = {'customer_name' : res[6]}
        customer_type = {'customer_type' : res[7]}
        expiration_apikey = {'expiration_apikey' : datetime.datetime.fromtimestamp(res[8]).strftime("%d-%m-%Y %I:%M:%S")}
        cnx_counter = {'cnx_counter' : int(res[1])}
        cnx_date = {'cnx_date' : list(res[2].split("+++"))}
        ip_addr = {'ip_address': list(res[3].split("+++"))}
        devices = {'device': list(res[4].split("+++"))}
        city = {'city': list(res[5].split("+++"))}
        data = [email,customer_name,customer_type,expiration_apikey, cnx_counter, cnx_date,ip_addr,devices,city]
        result.append(data)
    return result


def text_training_retrieve_json(excel_path, customer_name, customer_type, customer_universe, project_name):
    send_email_when_training_started(customer_name, project_name, 'classification', 'Apprentissage lancé!')
    if project_name:
        operation = 'training_classification'
    else:
        operation = 'training_text_detection'
    response = api.apipost(operation, customer_name, customer_type, project_name, excel_path,
                               customer_universe)
    result = json.loads(response.text)
    if int(result['status']) < 1:
        return True
    else:
        return False


def predict_customer(excel_path, customer_name, customer_type, customer_universe):
    response = api.apiget('predict_customer', customer_name, customer_type, customer_universe, excel_path)
    if response == 'True':
        return True
    else:
        return False


def new_similars(customer_name, customer_type, project_name, image, adress_ip):
    try:
        similars = api.apiget('get_similars', customer_name, customer_type, project_name, image)
        response = json.loads(similars)
        if response['response']['similars'] != []:
            today = datetime.date.today().strftime("%Y-%m-%d")
            image_domain = (tldextract.extract(image)).domain
            db.insert_or_update_into_table_history('client_history_table', today, customer_name, customer_type, project_name, image,
                                     'search_similars', json.dumps(response), response['category'], ip_adress = adress_ip,domain_url=image_domain , type_reference="")
        return json.dumps(response)
    except Exception as e:
        print('Exception %s' %e)
