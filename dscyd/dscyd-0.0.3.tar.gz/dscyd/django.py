from django.shortcuts import render, redirect

'django 开发需要用到的一些简单方法'

__author__ = 'dusc'


def page_aop_(func):
    '''
        分页功能, 装饰器, django的 view方法返回值是查询对象和模版, 或者是JsonResponse
    '''
    def view(request, *args, **kwargs):
        
        pagesize = int(request.POST.get('pagesize','10'))
        page = int(request.POST.get('page','1'))
        
        result = func(request, *args, **kwargs)

        if isinstance(result, tuple):
            print(result)
            res = result[0]
            res['pagesize'] = pagesize
            res['page'] = page
            print(res)
            paginator = Paginator(res['objects'], pagesize) 
            try:
                res['objects'] = paginator.page(page)
            except EmptyPage:
                res['objects'] = paginator.page(paginator.num_pages) 
            return render(request, result[1], res)

        elif isinstance(result, JsonResponse):
            return result

    view.__name__ = func.__name__

    return view


def login_(request, User, login='login.html'):
    '''
        登录判定
    '''
    user_name = request.POST.get('user_name', '')
    password = request.POST.get('password', '')

    user = User.objects.filter(user_name=user_name, password=password).first()
    if user:
        request.session['user_id'] = user.id
    else:
        return render(request, login, {'error': '用户名或密码错误!'})


def logout_(request, redirect_to='/login/'):
    '''
        退出登录
    '''
    del(request.session['user_id'])

    return redirect(redirect_to)


def check_user_(func, redirect_to='/login/'):
    '''
        检查用户是否登录
    '''
    def view(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return redirect(redirect_to)

        func(request, *args, **kwargs)

    view.__name__ = func.__name__

    return view


def save_obj_(obj,request):
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


def save_imgurl_(url):
    pass
