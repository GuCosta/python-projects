# Programa Assistente para Falar

# importing the pyttsx library
import pyttsx3

# initialization
engine = pyttsx3.init() #object criation

# Configurating speaking rate
#rate = engine.getProperty('rate') # getting details of current speaking rate
#print(rate)
engine.setProperty('rate', 180) # setting up new voice rate

# Configurating volume leverl
#volume = engine.getProperty('volume') # getting to know current volume level (min=0 and max=1)
#print(volume)
engine.setProperty('volume', 1.0) # setting up volume level  between 0 and 1

# Configurating speaking voice
voices = engine.getProperty('voices') # getting details of current voice
engine.setProperty('voice', voices[0].id) # changing index, changes voices. 0 for PT-BR_MARIA
#engine.setProperty('voice', voices[1].id) # changing index, changes voices. 1 for EN-US_ZIRA

def boas_vindas():
    print('Bem-vindo a sua assistente para falar')
    print('Para começar, digite seu texto e aperte a tecla ENTER')

def processar_fala(texto):
    engine.say(texto)
    engine.runAndWait()
    engine.stop()

def encerrar_programa():
    print('\nFoi um prazer ter sido sua assistente')
    print('Até a próxima')
    print('\nEncerrando o programa...')

# Saving Voice to a file
def salvar_fala(texto):
    # On linux make sure that 'espeak' and 'ffmpeg' are installed
    # engine.save_to_file(texto, 'test.mp3')
    # engine.runAndWait()
    
boas_vindas()    
texto = input()
sair = False 
while not sair:
    if texto != 'quit':
        processar_fala(texto)
        print('\nPara sair, digite \'quit\'')
        print('Para continuar falando, digite seu texto')
        texto = input()
    else:
        encerrar_programa()
        sair = True


