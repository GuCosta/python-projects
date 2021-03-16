import random

# Imprime a pontuação do jogador e do computador
def print_score(player_score, computer_score):
    print('')
    print('Score: Player ' + str(player_score) ' | Computer ' + str(computer_score))
    print('') 

# Imprime a escolha do jogador e do computador 
def print_choise(player_choice, computer_choice):
    print('Player: ' + player_choice)
    print('Computer: ' + computer_choice)

# Define o vencedor do jogo ou empate
def game_winner(player_choice, computer_choice):
    if player_choice == 'Rock' and computer_choice == 'Scissors' or \
    player_choice == 'Paper' and computer_choice == 'Rock' or \
    player_choice == 'Scissors' and computer_choice == 'Paper':
        return 'player'
    elif player_choice == computer_choice:
        return 'tie'
    else:
        return 'computer'

# Função principal para jogar
def play_game():
    game_list = ['Rock', 'Paper', 'Scissors'] # opções de escolha
    computer_score = 0 # pontuação inicial do computador
    player_score = 0 # pontuação inicial do jogador

    print_score(player_score, computer_socre) # imprime a pontuação inicial

    # Continua no loop até o usúario quiser sair
    run = True
    while run:
        computer_choice = random.choice(game_list) # escolha do computador é feita de forma aleatória
        player_choice = input('\nChoose Rock, Paper, Scissors or Quit: ')
        player_choice = player_choice.capitalize() # permite que a entrada do usuário seja válida no programa

        if player_choice == 'Quit':
            break
        elif player_choice in game_list:
            print_choise(player_choice, computer_choice)
            winner = game_winner(player_choice, computer_choice)
            if winner == 'player':
                print('Player won!')
                player_score += 1
            elif winner == 'computer':
                print('Computer won!')
                computer_score += 1
            else:
                print('Tie')
        else:
            print('Ops! Wrong command!')

    print_score(player_score, computer_socre) # imprime a pontuação final

play_game()