from django.shortcuts import render,redirect, get_object_or_404
from .forms import LoginForm, RegisterForm, ProfilePictureForm, ReceptForm, IngredientsForm
from .models import ProfilePictureModel, FriendsRequestModel, FriendListModel, ReceptModel, Ingredients
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required



# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            edit_form = form.save(commit=False)
            edit_form.first_name = edit_form.first_name.title()
            edit_form.last_name = edit_form.last_name.title()
            edit_form.email = edit_form.email.lower()
            edit_form.username = edit_form.username.lower()
            edit_form.save()
            return HttpResponseRedirect('/')
        else:
            form = RegisterForm()
            messages.error(request, 'Došlo k chybě při registraci!')
            return render(request, 'appconnext/register.html', {
            'form': form
        })
    if request.user.is_authenticated:
        return HttpResponseRedirect('main-page')
    else:
        form = RegisterForm()
        return render(request, 'appconnext/register.html', {
            'form': form
        })
    
# NAČÍTÁNÍ SVÉHO PROFILU
@login_required
def profile(request):
    if request.method == "POST":
        if 'update-picture' in request.POST:
            form = ProfilePictureForm(request.POST, request.FILES)
            if form.is_valid():
                edit_form = form.save(commit=False)
                edit_form.username = request.user.username
                existing_picture = ProfilePictureModel.objects.filter(username=request.user.username)
                if existing_picture:
                    existing_picture.delete()
                edit_form.save()
                return HttpResponseRedirect('my-profile')
            else:
                return HttpResponseRedirect('main-page')
            
        # přijmutí žádosti o přátelství
        elif 'accept-friend' in request.POST:
            person = request.POST.get('decline-friend-username')
            FriendListModel.objects.get_or_create(profile=request.user.username, friend=person)
            FriendListModel.objects.get_or_create(profile=person, friend=request.user.username)
            delete_request = FriendsRequestModel.objects.get(request_sender=person, request_receiver=request.user.username)
            delete_request.delete()
        # odmítnutí žádosti o přátelství
        elif 'decline-friend' in request.POST:
            person = request.POST.get('decline-friend-username')
            delete_request = FriendsRequestModel.objects.get(request_sender=person, request_receiver=request.user.username)
            delete_request.delete()
    
    # načti mi moje žádosti o přátelství, pokud žádné nemam, dej mi tam model at to muzu poslat do html a nemam chybu s prazdnou proměnnou
    all_requests = []
    requests = FriendsRequestModel.objects.filter(request_receiver=request.user.username)
    if requests:
        for one_request in requests: # jaká osoba mi poslala žádost o přátelství
            requests = User.objects.get(username=one_request.request_sender)
            all_requests.append(requests)        
    else:
        all_requests = FriendsRequestModel.objects.filter(request_sender='qetuoadgjlycbm')

    # načíst profilový obrázek
    profile_picture = ProfilePictureModel.objects.filter(username=request.user.username)
    profile_picture_form = ProfilePictureForm()
    # načíst počet přátel
    friends_count = FriendListModel.objects.filter(profile=request.user.username).count()
    # načíst počet příspěvků
    recept_count = ReceptModel.objects.filter(user_id=request.user.id).count()

    return render(request, 'appconnext/profile.html', {
        'profile_picture': profile_picture,
        'form': profile_picture_form,
        'friends_requests': all_requests,
        'friends_count': friends_count,
        'recept_count': recept_count
    })

# VYHLEDÁVÁÍ OSTATNÍCH UŽIVATELŮ
@login_required
def search_friends(request):
    matching_user = set() #proměnná na ukladání modelů s existujicimi vyhledavanymi uzivateli
    pictures = set() #proměnná na ukladání modelů s profilovkami → oboje jsou set aby byly unikátní
    if request.method == "POST":
        form = request.POST.get('search')
        check_search = form.strip()
        check_search = check_search.split(' ')
        for one_search in check_search:
            match = User.objects.filter(
                Q(first_name__iexact=one_search) |
                Q(last_name__iexact=one_search) |
                Q(username__iexact=one_search)
                )
            if match.exists():
                for user in match:
                    matching_user.add(user)

            # ukladani existujicich uzivatelu - respektive jejich profilovek
            for one_match in match:
                profile = ProfilePictureModel.objects.filter(username=one_match.username)
                if profile.exists():
                    for one_profile in profile:
                        pictures.add(one_profile)
            picture_dic = {pic.username: pic for pic in pictures}             

        return render(request, 'appconnext/search-friends.html', {
            'matching_users_result': matching_user,
            'profile_picture': pictures,
            'picture_dic': picture_dic
        })
    else:
        return render(request, 'appconnext/search-friends.html')

# osobní profil ostatních uživatelů
@login_required
def profile_detail(request, slug):
    one_user = User.objects.get(username=slug)
    if request.method == "POST":

        # odeslani zadosti o pratelstvi
        if 'send-request' in request.POST:
            send_request = FriendsRequestModel.objects.get_or_create(request_sender=request.user.username, request_receiver=one_user.username)

            # zruseni odeslane zadosti o pratelstvi
        elif 'remove-request' in request.POST:
            remove_request = FriendsRequestModel.objects.get(request_sender=request.user.username, request_receiver=one_user.username)
            remove_request.delete()

                # přijmutí žádosti o přátelství
        elif 'accept-friend' in request.POST:
            FriendListModel.objects.get_or_create(profile=request.user.username, friend=one_user.username)
            FriendListModel.objects.get_or_create(profile=one_user.username, friend=request.user.username)
            delete_request = FriendsRequestModel.objects.get(request_sender=one_user.username, request_receiver=request.user.username)
            delete_request.delete()

        # odmítnutí žádosti o přátelství
        elif 'decline-friend' in request.POST:
            delete_request = FriendsRequestModel.objects.get(request_sender=one_user.username, request_receiver=request.user.username)
            delete_request.delete()

        # odebrání uživatele z přátel
        elif 'remove-friend' in request.POST:
            delete_friend = FriendListModel.objects.get(profile=request.user.username, friend=one_user.username)
            delete_friend.delete()
            delete_friend = FriendListModel.objects.get(profile=one_user.username, friend=request.user.username)
            delete_friend.delete()

    # pokud to není můj profil, zobraz detail jiného profilu   
    if one_user.username != request.user.username:

        # načíst počet přátel
        count = FriendListModel.objects.filter(profile=one_user.username).count()
        if count:
            pass
        else:
            count = 0

        # načíst počet přidaných receptů
        recept_count = ReceptModel.objects.filter(user_id=one_user.id).count()
        if recept_count:
            pass
        else:
            recept_count = 0
            

        # zjisti jestli jsme už přátelé - na základě toho se pod profilem zobrazi bud pratele, pridat do pratel,...
        sent_requests = FriendListModel.objects.filter(profile=request.user.username, friend=one_user.username)
        if sent_requests:
            pass
        else:
        # zjistit jestli uz je odeslaná žádost o pratelstvi se zobrazovanou osobou, pokud ne, dej mi do modelu model, ať není prazdny a muzu ho poslat
            sent_requests = FriendsRequestModel.objects.filter(request_sender=request.user.username, request_receiver=one_user.username)
            if sent_requests:
                pass
            else: # zjistit jestli nemam zadost ja od něj
                sent_requests = FriendsRequestModel.objects.filter(request_sender=one_user.username, request_receiver=request.user.username)
                if sent_requests:
                    pass
                else: # pokud nemam napln mi promennou at muzu poslat
                    sent_requests = FriendsRequestModel.objects.filter(request_sender='qetuoadgjlycbm')

        try: # pokud má uzivatel profilovku, dej mi model do html s fotkou
            profile_picture = ProfilePictureModel.objects.get(username=one_user)
            if profile_picture:
                return render(request, 'appconnext/profile-detail.html', {
                    'one_user': one_user,
                    'profile_picture': profile_picture,
                    'friends': sent_requests,
                    'friends_count': count,
                    'recept_count': recept_count
                })
        except:
            #pokud uzivatel nema profilovku, nedavej mi zadny model do html
            return render(request, 'appconnext/profile-detail.html', {
                'one_user': one_user,
                'friends': sent_requests,
                'friends_count': count,
                'recept_count': recept_count
            })
    else:
        return HttpResponseRedirect('/my-profile')


# seznám přátel každého uživatele
@login_required
def friends_list(request, slug):
    all_friends = [] #seznam přátel
    pictures = [] #profilove obrazky pro kazdeho přítele
    picture_dic = {} # definuji slovnik, kdyby v něm nic neskoncilo, at se posle i tak
    one_user = User.objects.get(username=slug)
    friends = FriendListModel.objects.filter(profile=one_user)
    if friends:
        for one_friend in friends:
            all_friends.append(User.objects.get(username=one_friend.friend)) # seznam přátel

            one_picture = ProfilePictureModel.objects.filter(username=one_friend.friend) # načtení profilu s fotkou
            if one_picture.exists():
                pictures.append(one_picture[0])
        picture_dic = {pic.username: pic for pic in pictures}      

    else:
        all_friends = None
    return render(request, 'appconnext/friends-list.html', {
        'friends_list': all_friends,
        'one_user': one_user, 
        'profile_picture': pictures, # modely s profilovkama
        'picture_dic': picture_dic, #dictionary pro kontrolu jestli jsou profilovkxy, pokud jo tak budu nactat modely s fotkama (profile_picture)
    })




# obsah stranky
@login_required
def main_page(request):
    all_food = ReceptModel.objects.filter(user_id=request.user.id).order_by('title')
    return render(request, 'appconnext/main-page.html', {
        'all_food': all_food
    })

# přidat recept 
@login_required
def add_meal(request):
    if request.method == 'POST':
        form = ReceptForm(request.POST, request.FILES)
        if form.is_valid():
            food = form.save(commit=False)
            food.user_id = request.user.id
            food.save()
            parts = food.ingredients.split('\r\n') #VYTVORENI INGREDIENCE DO VYHLEDAVACE
            for one_part in parts:
                result = ' '.join(one_part.split())
                ingredient = Ingredients.objects.filter(name=result.lower()).first()
                if not ingredient:
                    Ingredients.objects.get_or_create(name=result.lower(), user_id=request.user.id)  #VYTVORENI INGREDIENCI DO VYHLEDAVAN
            return redirect(f'/main-page/detail-food/{food.id}')
        
        else:
            return redirect('add-meal')
    else:
        form = ReceptForm()
        return render(request, 'appconnext/add-meal.html', {
            'form': form
        })

# editovat recept
@login_required
def edit(request, id):
    edit_model = get_object_or_404(ReceptModel, id=id, user_id=request.user.id)
    if request.method == 'POST':
        form = ReceptForm(request.POST, request.FILES, instance=edit_model)
        if form.is_valid():
            food = form.save(commit=False)
            food.user_id = request.user.id
            food.save()
            parts = food.ingredients.split('\r\n') #VYTVORENI INGREDIENCE DO VYHLEDAVACE
            for one_part in parts:
                result = ' '.join(one_part.split())
                Ingredients.objects.get_or_create(name=result.lower())  #VYTVORENI INGERIENCI DO VYHLEDAVAN

            return redirect(f'/main-page/detail-food/{id}')
        else:
            return redirect(f'/main-page/{id}')
    else:
        form = ReceptForm(instance=edit_model)
        return render(request, 'appconnext/edit-food.html', {
            'form': form,
            'food_detail': edit_model
        })
    
# smazat recept
@login_required  
def delete(request,id):
    delete_model = get_object_or_404(ReceptModel, id=id)
    delete_model.delete()
    return redirect('main-page')

# datail receptu
@login_required
def detail_food(request, id):
    food = get_object_or_404(ReceptModel, id=id, user_id=request.user.id)
    return render(request, 'appconnext/detail-food.html', {
        'food': food
    })


# filtrovat jidla podle ingredienci
login_required
def select_food(request):
    if request.method == "POST":         
        if 'delete-ingredients' in request.POST:
            form_result = IngredientsForm(request.POST, user=request.user)
            if form_result.is_valid():
                selected_ingredients = form_result.cleaned_data['ingredients_selection']
                all_data = [ingredient.name for ingredient in selected_ingredients]
                for one_data in all_data:
                    remove_model = Ingredients.objects.filter(name=one_data)
                    remove_model.delete()
                return redirect('/select-food')
            else:
                return redirect('/select-food')

        elif 'select-ingredients' in request.POST:
            form = IngredientsForm(request.POST, user=request.user)
            if form.is_valid():
                selected_ingredients = form.cleaned_data['ingredients_selection']
                all_data = [ingredient.name for ingredient in selected_ingredients]
                query = Q()
                for one_ingredient in all_data:
                    query &= Q(ingredients__icontains=one_ingredient)
                food = ReceptModel.objects.filter(query, user_id=request.user.id).order_by('title')
                return render(request, 'appconnext/filter-food.html', {
                    'all_food': food
                })
            else:
                return HttpResponseRedirect('/select-food')
            
    else:
        select_ingredients = IngredientsForm(user=request.user)
        return render(request, 'appconnext/select-food.html', {
           'select_ingredients': select_ingredients
        })
    
@login_required
def friend_food_list(request, slug):
    one_user = User.objects.get(username=slug)
    recepts = ReceptModel.objects.filter(user_id=one_user.id)
    friend = FriendListModel.objects.filter(profile=request.user.username, friend=one_user.username)

    return render(request, 'appconnext/friend-food.html', {
        'one_user': one_user,
        'recept_list': recepts,
        'is_friend': friend
    })