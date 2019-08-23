def _save_attr_(obj,request):
	'''
		django接收request参数, 单表保存
		param: obj, django models object
		param: request, django request
	'''
    fields = obj._meta.fields

    for field in fields:
        field_name = field.name
        value = request.POST.get(field_name, '')
        if value:
            obj.__setattr__(field_name, value)
        else:
            value = request.FILES.get(field_name, '')
            if value:
                obj.__setattr__(field_name, value)
    obj.save()

