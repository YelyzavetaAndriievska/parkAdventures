from django.shortcuts import render

#from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Player, ModeratorPermissions
from .forms import RegistrationForm
from .forms import ResourceInputForm
from django.http import JsonResponse
from io import BytesIO
from PIL import Image
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import Player, PlayerStatus
from django.contrib.auth.models import User
import time

last_collected_time = {}

def is_moderator(user):
    return user.userprofile.user_type == 'moderator'

@user_passes_test(is_moderator)
def moderator_view(request):
    players = Player.objects.filter(user__is_active=True)
    if request.method == "POST":
        player_id = request.POST.get("player_id")
        action = request.POST.get("action")
        player_status = PlayerStatus.objects.get(player_id=player_id)
        player_status.can_play = (action == "enable")
        player_status.save()
        return redirect('moderator_view')
    return render(request, 'moderator.html', {'players': players})
def is_superadmin(user):
    return user.userprofile.user_type == 'superadmin'

@user_passes_test(is_superadmin)
def superadmin_view(request):
    moderators = User.objects.filter(userprofile__user_type='moderator')
    if request.method == "POST":
        moderator_id = request.POST.get("moderator_id")
        action = request.POST.get("action")
        permission = ModeratorPermissions.objects.get(moderator_id=moderator_id)
        permission.can_manage_players = (action == "enable")
        permission.save()
        return redirect('superadmin_view')
    return render(request, 'superadmin.html', {'moderators': moderators})




def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user, password = form.save()
            Player.objects.create(user=user)
            return render(request, 'registration_success.html', {'username': user.username, 'password': password})
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})




@login_required
def game_view(request):
    player = Player.objects.get(user=request.user)
    battle_mode = False
    message = player.log
    if 'sword_clicks' not in request.session:
        request.session['sword_clicks'] = 0

    sword_clicks = request.session['sword_clicks']

    # Функція для оновлення тексту повідомлення
    def update_log(text):
        nonlocal message
        player.log = ""  # Очищаємо лог щоб не дублювалося повідомлення при перезавантаженні сторінки
        player.log += text
        message = player.log

    # Функція для обробки бою з драконом
    def handle_battle(action):
        nonlocal sword_clicks
        if action == 'flash' and player.flash:
            player.dragon_life -= 20
            player.life -= 20
            player.flash -= 1
            update_log("You: take 20 damage!\n")
        elif action == 'elixir' and player.elixir > 0:
            player.life = 100
            player.life -= 20
            player.elixir -= 1
            update_log("You: take 100 life\n")
        elif action == 'magic_sword' and player.magic_sword:
            player.dragon_life -= 10
            sword_clicks += 1
            apply_shield_damage(10)
            check_sword_clicks('magic_sword')
        elif action == 'sword' and player.sword:
            player.dragon_life -= 5
            sword_clicks += 1
            apply_shield_damage(5)
            check_sword_clicks('sword')

    # Функція для обробки пошкодження щита
    def apply_shield_damage(base_damage):
        if player.magic_shield:
            player.life -= 10
            update_log("You: lose 10 life\n")
        elif player.shield:
            player.life -= 15
            update_log("You: lose 15 life\n")
        else:
            player.life -= 20
            update_log("You: lose 20 life\n")

    # Функція для перевірки кліків мечем
    def check_sword_clicks(action_type):
        nonlocal sword_clicks
        if sword_clicks >= 10:
            setattr(player, action_type, getattr(player, action_type) - 1)
            update_log(f"You: lose {action_type}\n")
            sword_clicks = 0
            if player.magic_shield:
                player.magic_shield -= 1
                update_log("You: lose magic shield!\n")
            elif player.shield:
                player.shield -= 1
                update_log("You: lose shield!\n")

    # Функція для покупки будівель і предметів
    def purchase_item(action, cost):
        for resource, amount in cost.items():
            if getattr(player, resource) < amount:
                return False
        for resource, amount in cost.items():
            setattr(player, resource, getattr(player, resource) - amount)
        setattr(player, action, getattr(player, action) + 1)
        update_log(f"You: buy the {action}!\n")
        return True
    def process_qr_code_data(request):
        if request.method == 'POST':
            resource_input = request.POST.get('resource_input')
            resource_map = {
                'wood_1': 'wood', 'iron_1': 'iron', 'gold_1': 'gold',
                'wood_2': 'wood', 'iron_2': 'iron', 'gold_2': 'gold',
                'wood_3': 'wood', 'iron_3': 'iron', 'gold_3': 'gold',
                'wood_4': 'wood', 'iron_4': 'iron', 'gold_4': 'gold',
                'wood_5': 'wood', 'iron_5': 'iron', 'gold_5': 'gold',
                'wood_6': 'wood', 'iron_6': 'iron', 'gold_6': 'gold',
            }

            if resource_input in resource_map:
                resource_type = resource_map[resource_input]
                current_time = time.time()

                # Перевіряємо, чи збирали цей ресурс протягом останньої хвилини
                if resource_input in last_collected_time:
                    time_since_last_collection = current_time - last_collected_time[resource_input]

                    if time_since_last_collection < 60:  # Менше 1 хвилини
                        remaining_time = 60 - time_since_last_collection
                        update_log(f"You: Cannot collect {resource_type} yet. Try again in {remaining_time:.1f} seconds.\n")
                        return  # Зупиняємо виконання, якщо час ще не минув

                # Оновлюємо час збору ресурсу
                last_collected_time[resource_input] = current_time

                # Збираємо ресурс
                setattr(player, resource_type, getattr(player, resource_type) + 1)
                update_log(f"You: find 1 {resource_type}!\n")

    
    
    if request.method == 'POST':
        action = request.POST.get('action')
        battle_mode = 'battle_mode' in request.POST

        if action in ['castle', 'forge', 'magic', 'wood', 'iron', 'gold', 'life', 'shield', 'magic_shield', 'sword',
                      'magic_sword', 'elixir', 'flash']:
            if battle_mode and action in ['shield', 'magic_shield', 'sword', 'magic_sword', 'elixir', 'flash']:
                handle_battle(action)
                if player.dragon_life <= 0:
                    reset_game(player)
                    battle_mode = False
                    update_log(f"You: win!\n")
                elif player.life <= 0:
                    reset_game(player)
                    battle_mode = False
                    update_log(f"You: lose!\n")
                else:
                    handle_battle(action)
            else:
                if action == 'castle' and not player.castle and player.wood > 4:
                    purchase_item('castle', {'wood': 5})
                elif action == 'castle' and player.castle:
                    update_log(f"You can`t buy more then one castle\n")
                elif action == 'castle' and not player.castle and player.wood < 5:
                    update_log(f"You need more wood to buy castle\n")
                elif action == 'forge' and player.wood > 3 and player.iron > 4 and not player.forge and player.castle:
                    purchase_item('forge', {'wood': 4, 'iron': 5})
                elif action == 'forge' and player.wood < 4 and not player.forge:
                    update_log(f"You need more wood to buy forge\n")
                elif action == 'forge' and player.iron < 5 and not player.forge:
                    update_log(f"You need more iron to buy forge\n")
                elif action == 'forge' and not player.castle and not player.forge:
                    update_log(f"You need to have a castle to buy forge\n")
                elif action == 'forge' and player.forge:
                    update_log(f"You can`t buy more then one forge\n")
                elif action == 'magic' and player.wood > 2 and player.iron > 3 and player.gold > 4 and player.forge and not player.magic:
                    purchase_item('magic', {'wood': 3, 'iron': 4, 'gold': 5})
                elif action == 'magic' and player.wood < 3 and not player.magic:
                    update_log(f"You need more wood to buy magic\n")
                elif action == 'magic' and player.iron < 4 and not player.magic:
                    update_log(f"You need more iron to buy magic\n")
                elif action == 'magic' and player.gold < 5 and not player.magic:
                    update_log(f"You need more gold to buy magic\n")
                elif action == 'magic' and not player.forge and not player.magic:
                    update_log(f"You need to have a forge to buy magic\n")
                elif action == 'magic' and player.magic:
                    update_log(f"You can`t have more then one magic\n")
                elif action in ['shield', 'magic_shield', 'sword', 'magic_sword', 'elixir', 'flash']:
                    # Перевірки для виготовлення предметів
                    if action == 'shield' and player.forge and player.wood > 1 and player.iron > 1:
                        purchase_item('shield', {'wood': 2, 'iron': 2})
                    elif action == 'shield' and player.forge and player.wood < 2:
                        update_log(f"You need more wood to buy a shield\n")
                    elif action == 'shield' and player.forge and player.iron < 2:
                        update_log(f"You need more iron to buy a shield\n")
                    elif action == 'shield' and not player.forge:
                        update_log(f"You need forge to buy a shield\n")
                    elif action == 'magic_shield' and player.magic and player.wood > 1 and player.iron > 1 and player.gold > 1:
                        purchase_item('magic_shield', {'wood': 2, 'iron': 2, 'gold': 2})
                    elif action == 'magic_shield' and not player.magic:
                        update_log(f"You need magic to buy a magic shield\n")
                    elif action == 'magic_shield' and player.magic and player.wood < 2:
                        update_log(f"You need more wood to buy a magic shield\n")
                    elif action == 'magic_shield' and player.magic and player.iron < 2:
                        update_log(f"You need more iron to buy a magic shield\n")
                    elif action == 'magic_shield' and player.magic and player.gold < 2:
                        update_log(f"You need more gold to buy a magic shield\n")
                    elif action == 'sword' and player.forge and player.wood > 1 and player.iron > 1:
                        purchase_item('sword', {'wood': 2, 'iron': 2})
                    elif action == 'sword' and not player.forge:
                        update_log(f"You need forge to buy a sword\n")
                    elif action == 'sword' and player.forge and player.wood < 2:
                        update_log(f"You need more wood to buy a sword\n")
                    elif action == 'sword' and player.forge and player.iron < 2:
                        update_log(f"You need more iron to buy a sword\n")
                    elif action == 'magic_sword' and player.magic and player.wood > 1 and player.iron > 1 and player.gold > 1:
                        purchase_item('magic_sword', {'wood': 2, 'iron': 2, 'gold': 2})
                    elif action == 'magic_sword' and not player.magic:
                        update_log(f"You need magic to buy a magic sword\n")
                    elif action == 'magic_sword' and player.magic and player.wood < 2:
                        update_log(f"You need more wood to buy a magic sword\n")
                    elif action == 'magic_sword' and player.magic and player.iron < 2:
                        update_log(f"You need more iron to buy a magic sword\n")
                    elif action == 'magic_sword' and player.magic and player.gold < 2:
                        update_log(f"You need more gold to buy a magic sword\n")
                    elif action == 'elixir' and player.magic and player.gold > 4:
                        purchase_item('elixir', {'gold': 5})
                    elif action == 'elixir' and not player.magic:
                        update_log(f"You need magic to buy elixir\n")
                    elif action == 'elixir' and player.magic and player.gold < 5:
                        update_log(f"You need more gold to buy elixir\n")
                    elif action == 'flash' and player.magic and player.wood > 1 and player.iron > 1 and player.gold > 2:
                        purchase_item('flash', {'wood': 2, 'iron': 2, 'gold': 3})
                    elif action == 'flash' and not player.magic:
                        update_log(f"You need magic to buy flash\n")
                    elif action == 'flash' and player.wood < 2:
                        update_log(f"You need more wood to buy flash\n")
                    elif action == 'flash' and player.iron < 2:
                        update_log(f"You need more iron to buy flash\n")
                    elif action == 'flash' and player.gold < 3:
                        update_log(f"You need more gold to buy flash\n")

        request.session['sword_clicks'] = sword_clicks

    # Обробка введеного символу
    process_qr_code_data(request)

    '''resource_input_form = ResourceInputForm(request.POST)
    if resource_input_form.is_valid():
        resource_input = resource_input_form.cleaned_data['input_text']
        resource_map = {'w': 'wood', 'i': 'iron', 'g': 'gold'}
        if resource_input in resource_map:
            resource_type = resource_map[resource_input]
            setattr(player, resource_type, getattr(player, resource_type) + 100)
            update_log(f"You: find 100 {resource_type}!\n")'''

    player.save()

    return render(request, 'game.html', {
        'player': player,
        'battle_mode': battle_mode,
        'message': message,
        'form': ResourceInputForm()
    })

# Функція для скидання гри
def reset_game(player):
    player.dragon_life = 100
    player.life = 100
    player.castle = 0
    player.forge = 0
    player.magic = 0
    player.wood = 0
    player.iron = 0
    player.gold = 0
    player.sword = 0
    player.magic_sword = 0
    player.shield = 0
    player.magic_shield = 0
    player.flash = 0
    player.elixir = 0
    player.log = ''
    