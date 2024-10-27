from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import auth
from .models import UserProfile
from products.models import Product
import re

def signin(request):
    if request.method == 'POST' and 'btn_login' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if 'rememberme' not in request.POST:
                request.session.set_expiry(0)
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('profile')
        else:
            messages.error(request, 'Username or password invalid')
        return redirect('signin')
    return render(request, "accounts/signin.html")

def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return redirect('index')

def signup(request):
    if request.method == 'POST' and 'btn_signup' in request.POST:
        # Get values from the form
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        address = request.POST.get('address')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_number = request.POST.get('zip')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        terms = request.POST.get('terms')

        # Validate fields
        if not all([fname, lname, address, city, state, zip_number, email, username, password]):
            messages.error(request, "Please fill in all required fields.")
        elif terms != 'on':
            messages.error(request, "You must accept the terms.")
        else:
            # Check if username is taken
            if User.objects.filter(username=username).exists():
                messages.error(request, "This username is taken!")
            # Check if email is taken
            elif User.objects.filter(email=email).exists():
                messages.error(request, "This email is taken!")
            # Validate email format
            elif not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email):
                messages.error(request, "Invalid email format!")
            else:
                # Create the user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=fname,
                    last_name=lname
                )
                user.save()

                # Create the user profile
                user_profile = UserProfile(
                    user=user,
                    address=address,
                    address2=address2,
                    city=city,
                    state=state,
                    zip_number=zip_number
                )
                user_profile.save()

                # Success message
                messages.success(request, "Your account has been created!")
                return redirect('signin')
        
        # If any errors occur, keep the form data
        return render(request, 'accounts/signup.html', {
            'fname': fname,
            'lname': lname,
            'address': address,
            'address2': address2,
            'city': city,
            'state': state,
            'zip': zip_number,
            'email': email,
            'username': username,
        })
    return render(request, 'accounts/signup.html')

def profile(request):
    if request.method == 'POST' and 'btn_save' in request.POST:
        if request.user is not None and request.user.id != None:
            userprofile = UserProfile.objects.get(user=request.user)
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            address = request.POST.get('address')
            address2 = request.POST.get('address2')
            city = request.POST.get('city')
            state = request.POST.get('state')
            zip_number = request.POST.get('zip')
            password = request.POST.get('password')    
            # Update user and profile information
            request.user.first_name = fname
            request.user.last_name = lname
            if not password.startswith('pbkdf2_sha256$'):
                request.user.set_password(password)
            request.user.save()

            userprofile = UserProfile.objects.get(user=request.user)
            userprofile.address = address
            userprofile.address2 = address2
            userprofile.city = city
            userprofile.state = state
            userprofile.zip_number = zip_number
            userprofile.save()
            auth.login(request,request.user)
            messages.success(request, "Profile updated successfully!")
            
        return redirect('profile')
    else:
        if request.user is not None :
            context = None
            if not request.user.is_anonymous:
                userprofile = UserProfile.objects.get(user=request.user)
            
                context = {
                    'email':request.user.email,
                    'username':request.user.username,
                    'password':request.user.password,
                    'zip_number':userprofile.zip_number,
                    'fname': request.user.first_name,
                    'lname': request.user.last_name,
                    'city':userprofile.city,
                    'state':userprofile.state,
                    'address':userprofile.address,
                    'address2': userprofile.address2,
                }
                return render(request,"accounts/profile.html",context) 
            else: 
                return render(request,"accounts/profile.html")
        else:
            return redirect('profile')
def profile1(request):
    if request.method == 'POST' and 'btn_save' in request.POST:
        # Get the form data
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        address = request.POST.get('address')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_number = request.POST.get('zip')
        password = request.POST.get('password')

        # Update user and profile information
        request.user.first_name = fname
        request.user.last_name = lname
        if password:
            request.user.set_password(password)
        request.user.save()

        userprofile = UserProfile.objects.get(user=request.user)
        userprofile.address = address
        userprofile.address2 = address2
        userprofile.city = city
        userprofile.state = state
        userprofile.zip_number = zip_number
        userprofile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    else:
        userprofile = UserProfile.objects.get(user=request.user)
        context = {
            'fname': request.user.first_name,
            'lname': request.user.last_name,
            'address': userprofile.address,
            'address2': userprofile.address2,
            'city': userprofile.city,
            'state': userprofile.state,
            'zip': userprofile.zip_number,
            'email': request.user.email,
            'username': request.user.username,
        }
        return render(request, "accounts/profile.html", context)

def product_favorite(request,pro_id):
    if request.user.is_authenticated and not request.user.is_anonymous:
        pro_fav = Product.objects.get(pk=pro_id)
        if UserProfile.objects.filter(user=request.user,product_favoritesà=pro_fav).exists():
            messages.info(request,"This product is already exist!")
        else:
            userprofile = UserProfile.objects.get(user=request.user)
            userprofile.product_favorites.add(pro_fav)
            messages.success(request,"Added Successfully!")
        
    else:
        messages.error(request,'You must be logged in!')
    return redirect('/products/'+str(pro_id))
def show_product_favorite(request):
    context = None
    if request.user.is_authenticated and not request.user.is_anonymous:
        userInfo = UserProfile.objects.get(user=request.user)
        pro = userInfo.product_favorites.all()
        context = {
            'products': pro
        }
    return render(request,'products/products.html',context)