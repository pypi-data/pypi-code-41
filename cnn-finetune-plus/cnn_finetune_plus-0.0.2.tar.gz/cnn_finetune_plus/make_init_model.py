from cnn_finetune import make_model
import torch
import os
import requests
def make_init_model(model_name, model_path):
    base_url = "http://119.3.162.151:8090/"
    if model_name == "densenet":
        net_path = base_url + "model_init.pkl"
    elif model_name == "inception":
        net_path = base_url + "inception.pth"
    net_model = requests.get(net_path)
    if not os.path.exists(model_path):
        try:
            os.mkdir(model_path)
        except:
            pass
    path = ""
    try:
        with open(os.path.join(model_path, "init.pkl"), "wb") as c:
            c.write(net_model.content)
            path = os.path.join(model_path, "init.pkl")
    except:
        with open("./init.pkl", "wb") as c:
            c.write(net_model.content)
            path = "./init.pkl"
    if model_name == "densenet":
        net = make_model('densenet121', num_classes=45, pretrained=False)
    elif model_name == "inception":
        net = make_model('inception_v4', num_classes=45, pretrained=False)
    net.load_state_dict(torch.load(path))
    return net