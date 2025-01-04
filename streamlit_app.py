import streamlit as st

# Funções auxiliares
def calcular_grids(max_price, min_price, num_grids):
    return (max_price - min_price) / num_grids

def sugerir_grids(volatilidade):
    if volatilidade > 20:
        return 10  # Alta volatilidade
    elif volatilidade > 10:
        return 20  # Média volatilidade
    else:
        return 30  # Baixa volatilidade

def calcular_alavancagem(capital):
    if capital <= 100:
        return 10  # Alto risco
    elif capital <= 1000:
        return 5  # Médio risco
    else:
        return 3  # Baixo risco

def simular_lucros(max_price, min_price, num_grids, capital, alavancagem):
    lucro_por_grid = (max_price - min_price) / num_grids * capital * alavancagem * 0.01
    return lucro_por_grid * num_grids

# Interface Streamlit
st.title("Gestor Diário de Robô de Grid Trading")

# Passo 1: Inserir ativos dinâmicos
st.header("1. Insira Ativos e suas Variações")
st.write("Adicione os ativos com base na sua análise diária ou informações externas.")

ativos = st.text_area(
    "Digite os ativos e suas variações (exemplo: BTCUSDT 12.5, ETHUSDT 8.3):",
    value="",
    placeholder="Exemplo: BTCUSDT 12.5\nETHUSDT 8.3",
)

ativo_list = []
if ativos:
    ativo_list = [linha.split() for linha in ativos.split("\n") if len(linha.split()) == 2]
    st.write("Ativos adicionados:")
    for ativo in ativo_list:
        st.write(f"- Ativo: {ativo[0]}, Variação: {ativo[1]}%")
else:
    st.warning("Adicione pelo menos um ativo para continuar!")

# Passo 2: Selecionar ativo a trabalhar
if ativo_list:
    st.header("2. Escolha o Ativo para Configurar")
    ativo_selecionado = st.selectbox("Selecione um ativo:", [ativo[0] for ativo in ativo_list])

    # Passo 3: Inserir preços máximos e mínimos
    st.header(f"3. Configurar Preços de {ativo_selecionado}")
    max_price = st.number_input(f"Preço Máximo de {ativo_selecionado}:", min_value=0.0, format="%.6f")
    min_price = st.number_input(f"Preço Mínimo de {ativo_selecionado}:", min_value=0.0, format="%.6f")
    volatilidade = ((max_price - min_price) / min_price) * 100 if max_price and min_price else 0.0

    # Passo 4: Configurar capital
    st.header("4. Insira o Capital Disponível")
    capital = st.number_input("Capital (USDT):", min_value=0.0, value=100.0)

    # Passo 5: Sugestões automáticas
    st.header("5. Configurações Automáticas")
    num_grids = sugerir_grids(volatilidade)
    grid_interval = calcular_grids(max_price, min_price, num_grids)
    alavancagem = calcular_alavancagem(capital)

    st.write(f"**Número de Grids Sugeridos:** {num_grids}")
    st.write(f"**Intervalo por Grid:** {grid_interval:.6f} USDT")
    st.write(f"**Alavancagem Sugerida:** {alavancagem}x")

    # Passo 6: Configurar Trail Stop e Take Profit
    st.header("6. Configuração de Lucros")
    trailing_stop = st.checkbox("Ativar Trailing Stop em Lucro", value=True)
    take_profit = st.slider("Porcentagem de Take Profit (%)", min_value=0.0, max_value=10.0, value=1.0)

    # Passo 7: Simulação de lucros
    st.header("7. Simulação de Resultados")
    lucro_estimado = simular_lucros(max_price, min_price, num_grids, capital, alavancagem)
    st.write(f"**Lucro Estimado por Grid Trading:** {lucro_estimado:.2f} USDT")

    # Confirmação final
    st.header("8. Confirmação e Aplicação")
    confirmar = st.button("Confirmar e Aplicar Configurações")
    if confirmar:
        st.success("Configuração aplicada com sucesso!")
        st.write("Resumo:")
        st.write(f"- Ativo: {ativo_selecionado}")
        st.write(f"- Máximo: {max_price}, Mínimo: {min_price}")
        st.write(f"- Capital: {capital} USDT")
        st.write(f"- Grids: {num_grids}")
        st.write(f"- Alavancagem: {alavancagem}x")
        st.write(f"- Trailing Stop: {'Ativado' if trailing_stop else 'Desativado'}")
        st.write(f"- Take Profit: {take_profit}%")
