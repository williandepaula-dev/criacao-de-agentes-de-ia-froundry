

    

import streamlit as st

st.title('BANCO')

saldo = 1000.00
extrato =  [1000.0]
acessar  =  st.text_input('Deseja acessar o banco? s/n')



# while acessar ==  's':


senha = '1234'
senha_input = st.text_input('Senha: ')

if st.button('Acessar...'):

    if senha_input == senha:

        st.header('Acesso autorizado...')
        menu =  ['','Saque','Deposito','Extrato']
         
        escolha = st.number_input('Escolha a operação')
        
        action = st.menu_button("Escolha", options=['Saque','Deposito','Extrato'])
        
        if action == 'Saque':
                
                saque =  st.number_input('Saque R$ >>> ')    
                saldo = saldo - saque
                st.write('R$', saldo)
                extrato.append(-saque)
             
            
        elif action == 'Deposito':
                
                deposito = st.number_input('Saque R$ >>> ')    
                saldo = saldo + deposito
                st.write('R$', saldo)
                extrato.append(deposito)
              
                
        elif action == 'Extrato':
                st.write('extrato', extrato)      
                
                
    else:
       st.text_input('Ate logo')
            
        
   