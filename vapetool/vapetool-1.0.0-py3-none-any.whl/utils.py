import re

def battery_id(battery) -> str:
    b = battery
    brand, model, chemistry, size, capacity = b['brand'], b['model'], b['chemistry'], b['size'], b['capacity']
    return re.sub('[^A-Za-z0-9_]+', '_', f'{brand}-{model}-{chemistry}-{size}-{capacity}')

def normalize_chemistry_and_name(battery):
    if battery['chemistry']: return
    model = battery['model']
    if 'IMR' in model or 'LMO' in model:
        battery['chemistry'] = "IMR"
        battery['model'] = model.replace('IMR','').replace('LMO','').strip()
        return

    if 'ICR' in model or 'LCO' in model:
        battery['chemistry'] = "ICR"
        battery['model'] = model.replace('ICR','').replace('LCO','').strip()
        return

    if 'INR' in model or 'NMC' in model:
        battery['chemistry'] = "INR"
        battery['model'] = model.replace('INR','').replace('NMC','').strip()
        return

    if 'IFR' in model or 'LFP' in model:
        battery['chemistry'] = "IFR"
        battery['model'] = model.replace('IFR','').replace('LFP','').strip()
        return

    if 'NCA' in model:
        battery['chemistry'] = "NCA"
        battery['model'] = model.replace('NCA','').strip()
        return

    if 'NCO' in model:
        battery['chemistry'] = "NCO"
        battery['model'] = model.replace('NCO','').strip()
        return
    
    if 'NCR' in model:
        battery['chemistry'] = "NCR"
        battery['model'] = model.replace('NCR','').strip()
        return

