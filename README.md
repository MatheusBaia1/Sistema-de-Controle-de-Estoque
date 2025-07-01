# 📦 Sistema de Controle de Estoque

## 📌 Sobre o Projeto

Este sistema foi desenvolvido com o objetivo de **organizar, automatizar e facilitar o controle de estoque** de produtos em geral. Ideal para quem busca uma solução prática para gerenciar entradas, saídas e níveis de estoque, de forma simples e eficiente.

## 🎯 Objetivo

Oferecer uma aplicação funcional que permita:

- Registrar entradas e saídas de produtos.
- Manter um histórico de movimentações.
- Cadastrar e gerenciar usuários.
- Monitorar níveis de estoque em tempo real.
- Emitir alertas automáticos para produtos com estoque crítico.
- Reduzir perdas, atrasos e falhas em registros manuais.

## ⚙️ Funcionalidades

- ✅ Cadastro de produtos  
- ✅ Registro de entradas e saídas de materiais  
- ✅ Edição e exclusão de movimentações  
- ✅ Alerta automático de estoque baixo  
- ✅ Exportação e importação de dados via CSV  
- ✅ Histórico completo de saídas  
- ✅ Sistema de login e controle de usuários  
- ✅ Interface gráfica intuitiva (CustomTkinter)  
- ✅ Banco de dados local com SQLite3  

## 🛠️ Tecnologias Utilizadas

- Python  
- CustomTkinter (Interface Gráfica)  
- SQLite3 (Banco de Dados)  
- CSV (Importação/Exportação de dados)  

---

## 📥 Regras para Importação de Produtos via CSV

Para utilizar corretamente a funcionalidade de **importação de produtos**, é necessário seguir a estrutura e o formato abaixo no arquivo `.csv`:

- A ordem das colunas deve ser exatamente:
  1. **Nome**
  2. **Descrição**
  3. **Quantidade**

- **Regras de formatação obrigatórias:**
  - Os títulos das colunas devem iniciar com **letra maiúscula**.
  - Os campos de texto (Nome e Descrição) devem conter a **acentuação correta** (ex.: "Descrição", "Câmara", "Evaporador").
  - A coluna **Quantidade** deve conter apenas **valores numéricos inteiros**.

> ⚠️ Arquivos fora desse padrão poderão causar erros na importação ou inserção incorreta dos dados.

---

## 🖼️ Demonstrações da Interface

**Tela de Login**  
![Login](https://github.com/user-attachments/assets/ecc37e92-53a1-4ecc-b7d4-9adc45e2ca21)

**Tela Principal**  
![TelaPrincipal](https://github.com/user-attachments/assets/38e6fc33-e7b9-4dd7-a741-8a8ffcc0b7c5)

**Tela de Cadastro de Usuário**  
![CadastroUsuario](https://github.com/user-attachments/assets/7fc3408a-9cbf-44d4-af1a-a68f82e17ec1)

**Tela de Cadastro de Produto**  
![CadastroProd](https://github.com/user-attachments/assets/11f5a55a-7a75-4199-b566-8976ef907dc9)

**Tela de Produtos**  
![Produtos](https://github.com/user-attachments/assets/1866aa7a-92b1-4d5d-89b2-09f3e3550334)

**Tela de Saída de Produtos**  
![RegistrarSaida](https://github.com/user-attachments/assets/622ce975-10ed-494e-94ae-2acc9a903a92)

**Tela de Remoção de Produto**  
![RemoverProd](https://github.com/user-attachments/assets/151ca3f7-47c8-4935-9d57-e6197eea9972)

**Tela de Alerta de Estoque Baixo**  
![EstoqueBaixo](https://github.com/user-attachments/assets/cebd728e-8a3a-4d2b-9b2b-3eb34acc161f)

**Tela de Histórico de Saídas**  
![HistoricoSaida](https://github.com/user-attachments/assets/54289827-8b61-4394-a979-0436d08ed4b1)
