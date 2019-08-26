def leave_one_out(cases, config):
    # Start leave-one-out cycling
    for i in range(config["n_loo"]):
        # Create a Convolutional Neural Network model
        model = MIScnn_NN.NeuralNetwork(config)
        # Choose a random sample
        loo = cases.pop(np.random.choice(len(cases)))
        # Train the model with the remaining cases
        model.train(cases)
        # Make a detailed validation on the LOO sample
        detailed_validation(model, [loo], str(loo), config)
