from Fortuna import *


if __name__ == "__main__":

    basic_matrix = {
        "A": range(1, 4, 1),
        "B": range(10, 40, 10),
        "C": range(100, 400, 100),
    }

    # Base case, essentially the same as FlexCat(basic_matrix, key_bias="quantum_linear", val_bias="quantum_linear")
    quantum_a = QuantumMonty(basic_matrix["A"]).quantum_linear  # val_bias
    quantum_b = QuantumMonty(basic_matrix["B"]).quantum_linear  # val_bias
    quantum_c = QuantumMonty(basic_matrix["C"]).quantum_linear  # val_bias
    nested_QM = QuantumMonty((quantum_a, quantum_b, quantum_c)).quantum_linear  # key_bias
    distribution_timer(nested_QM, label="Base Case, nested_QM()")
    print("Example call: result")
    print(f"nested_QM(): {nested_QM()}\n")

    basic_flex_cat = FlexCat(basic_matrix, key_bias="quantum_linear", val_bias="quantum_linear")
    distribution_timer(basic_flex_cat, label="basic_flex_cat()")
    print("Example call: result")
    print(f"basic_flex_cat(): {basic_flex_cat()}\n")

    lambda_matrix = {
        "A": (
            lambda x: x + 1,
            lambda x: x + 2,
            lambda x: x + 3,
        ),
        "B": (
            lambda x: x + 10,
            lambda x: x + 20,
            lambda x: x + 30,
        ),
        "C": (
            lambda x: x + 100,
            lambda x: x + 200,
            lambda x: x + 300,
        ),
    }

    # Base case, essentially the same as FlexCat(lambda_matrix, key_bias="quantum_linear", val_bias="quantum_linear")
    quantum_a = QuantumMonty(lambda_matrix["A"]).quantum_linear  # val_bias
    quantum_b = QuantumMonty(lambda_matrix["B"]).quantum_linear  # val_bias
    quantum_c = QuantumMonty(lambda_matrix["C"]).quantum_linear  # val_bias
    nested_lambda_QM = QuantumMonty((quantum_a, quantum_b, quantum_c)).quantum_linear  # key_bias
    distribution_timer(nested_lambda_QM, x=10, label="Base Case, nested_lambda_QM(x=10)")
    print("Example call: result")
    print(f"nested_lambda_QM(x=10): {nested_lambda_QM(x=10)}\n")

    lambda_flex_cat = FlexCat(lambda_matrix, key_bias="quantum_linear", val_bias="quantum_linear")
    distribution_timer(lambda_flex_cat, x=10, label="lambda_flex_cat(x=10)")
    print("Example call: result")
    print(f"lambda_flex_cat(x=10): {lambda_flex_cat(x=10)}\n")
