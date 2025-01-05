import streamlit as st

# Funções auxiliares
def calcular_tamanho_grid(max_price, min_price, num_grids):
    return (max_price - min_price) / num_grids if num_grids > 0 else 0

def calcular_num_grids(capital, tamanho_grid, alavancagem):
    if tamanho_grid <= 0:
        return 0
    capital_por_grid = tamanho_grid * alavancagem
    return int(capital / capital_por_grid)

def sugerir_grids(max_price, min_price, capital, alavancagem, max_grids=190, tamanho_grid_desejado=0.1):
    # Calcular a faixa de preço
    faixa_preco = max_price - min_price
    
    # Calcular o número de grids com base na faixa de preço e tamanho de grid
    grids_necessarios = faixa_preco / tamanho_grid_desejado
    
    # Ajustar o número de grids com base no capital e alavancagem
    capital_necessario_por_grid = tamanho_grid_desejado * (max_price + min_price) / 2  # Média do preço
    capital_total_necessario = capital_necessario_por_grid * grids_necessarios
    
    # Ajustar com a alavancagem
    capital_com_alavancagem = capital_total_necessario / alavancagem
    
    # Garantir que o número de grids não ultrapasse o máximo permitido
    grids_sugeridos = min(grids_necessarios, max_grids)
    
    # Calcular o número de grids possíveis com o capital disponível
    tamanho_grid = calcular_tamanho_grid(max_price, min_price, grids_sugeridos)
    num_grids_sugeridos = calcular_num_grids(capital, tamanho_grid, alavancagem)
    
    # Limitar o número de grids sugeridos a um valor realista (ex: entre 10 e 20 grids)
    num_grids_sugeridos = max(10, min(num_grids_sugeridos, max_grids))
    
    # Retornar os valores ajustados
    return num_grids_sugeridos, tamanho_grid

def determinar_modo_operacao(volume_hive, volume_usdt):
    """
    Determina se o mercado está em tendência de alta (LONG), baixa (SHORT) ou lateral (NEUTRAL).
    """
    if volume_hive > volume_usdt:
        return "LONG"
    elif volume_hive < volume_usdt:
        return "SHORT"
    else:
        return "NEUTRAL"

def converter_volume(volume_str):
    """
    Converte o volume inserido em formato K ou M para valor numérico.
    Exemplo: "10K" -> 10000, "2M" -> 2000000
    """
    volume_str = volume_str.upper().strip()
    if volume_str.endswith('K'):
        return float(volume_str[:-1]) * 1_000
    elif volume_str.endswith('M'):
        return float(volume_str[:-1]) * 1_000_000
    else:
        return float(volume_str)

# Interface Streamlit
st.title("Gestor Diário de Robô de Grid Trading - BitGet")

# Passo 1: Inserir dados do ativo
st.sidebar.header("1. Dados do Ativo")
ativo = st.sidebar.text_input("Nome do Ativo (ex.: HIVEUSDT):", placeholder="Digite o ativo", value="HIVEUSDT")
max_price = st.sidebar.number_input("Preço Máximo (24h):", min_value=0.0, format="%.6f")
min_price = st.sidebar.number_input("Preço Mínimo (24h):", min_value=0.0, format="%.6f")
volume_hive_str = st.sidebar.text_input("Volume HIVE (24h):", placeholder="Exemplo: 10K ou 2M", value="10K")
volume_usdt_str = st.sidebar.text_input("Volume USDT (24h):", placeholder="Exemplo: 10K ou 2M", value="10K")

# Converter volumes de HIVE e USDT
try:
    volume_hive = converter_volume(volume_hive_str)
    volume_usdt = converter_volume(volume_usdt_str)
except ValueError:
    st.error("Erro ao converter os volumes. Verifique se está usando o formato correto (K ou M).")

if ativo and max_price > min_price > 0:
    st.write(f"**Ativo Selecionado:** {ativo}")
    st.write(f"**Máximo (24h):** {max_price}")
    st.write(f"**Mínimo (24h):** {min_price}")
    st.write(f"**Volume HIVE (24h):** {volume_hive:.2f}")
    st.write(f"**Volume USDT (24h):** {volume_usdt:.2f}")

    # Determinar o modo de operação com base nos volumes
    modo_operacao = determinar_modo_operacao(volume_hive, volume_usdt)
    st.write(f"**Modo de Operação Sugerido:** {modo_operacao}")

    # Ajuste dos preços com base no modo de operação
    if modo_operacao == "LONG":
        novo_max_price = max_price + (max_price * 0.02)  # Ajuste baseado em 2% do preço máximo
        novo_min_price = min_price  # Mantém o mínimo inalterado
    elif modo_operacao == "SHORT":
        novo_max_price = max_price  # Mantém o máximo inalterado
        novo_min_price = min_price - (min_price * 0.02)  # Ajuste baseado em 2% do preço mínimo
    else:  # NEUTRAL
        novo_max_price = max_price + (max_price * 0.01)  # Ajuste baseado em 1% do preço máximo
        novo_min_price = min_price - (min_price * 0.01)  # Ajuste baseado em 1% do preço mínimo

    st.write(f"**Novo Máximo Sugerido:** {novo_max_price:.6f}")
    st.write(f"**Novo Mínimo Sugerido:** {novo_min_price:.6f}")

    # Passo 2: Configurar capital
    st.header("2. Insira o Capital Disponível")
    capital = st.number_input("Capital (USDT):", min_value=0.0, value=20.0)

    # Passo 3: Configurar Alavancagem
    st.header("3. Configurar Alavancagem")
    alavancagem = st.slider("Escolha a Alavancagem:", min_value=1, max_value=125, value=5)

    # Passo 4: Configurações automáticas
    st.header("4. Configurações Automáticas")
    nivel_risco = st.radio("Nível de Risco:", ["Baixo", "Médio", "Alto"], index=1)
    
    # Ajustar o tamanho por grid com base no nível de risco
    if nivel_risco == "Baixo":
        tamanho_grid_desejado = 0.05  # Menor risco, tamanho de grid menor
    elif nivel_risco == "Médio":
        tamanho_grid_desejado = 0.1  # Risco médio
    else:  # Alto
        tamanho_grid_desejado = 0.2  # Maior risco, tamanho de grid maior

    # Calcular o número de grids sugeridos
    num_grids_sugeridos, tamanho_grid = sugerir_grids(novo_max_price, novo_min_price, capital, alavancagem, tamanho_grid_desejado=tamanho_grid_desejado)
    
    st.write(f"**Número de Grids Sugeridos:** {num_grids_sugeridos}")
    st.write(f"**Tamanho por Grid:** {tamanho_grid:.6f} USDT")
    st.write(f"**Alavancagem Selecionada:** {alavancagem}x")    

    # Passo 5: Configurar Trail Stop e Take Profit
    st.header("5. Configuração de Lucros")
    trailing_stop = st.checkbox("Ativar Trailing Stop em Lucro", value=True)
    take_profit = st.slider("Porcentagem de Take Profit (%)", min_value=0.0, max_value=10.0, value=1.0)

    # Relatório final
    st.header("6. Relatório de Sugestões")
    st.write("**Resumo das Configurações Sugeridas:**")
    st.write(f"- **Modo de Operação:** {modo_operacao}")
    st.write(f"- **Novo Máximo Sugerido:** {novo_max_price:.6f}")
    st.write(f"- **Novo Mínimo Sugerido:** {novo_min_price:.6f}")
    st.write(f"- **Número de Grids Sugeridos:** {num_grids_sugeridos}")
    st.write(f"- **Tamanho por Grid:** {tamanho_grid:.6f} USDT")
    st.write(f"- **Alavancagem Selecionada:** {alavancagem}x")
    st.write(f"- **Trailing Stop Ativado:** {'Sim' if trailing_stop else 'Não'}")
    st.write(f"- **Take Profit Configurado:** {take_profit}%")
