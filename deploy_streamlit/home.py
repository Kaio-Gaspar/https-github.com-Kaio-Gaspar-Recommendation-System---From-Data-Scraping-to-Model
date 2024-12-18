import streamlit as st
import pandas as pd
import sqlite3
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Função para carregar dados do banco de dados SQLite
def load_data():
    """
    Carrega os dados de dois arquivos CSV: 'df2.csv' e 'df.csv'.
    O df2 contém os dados processados para cálculo da similaridade, enquanto o df contém os dados completos dos veículos.
    """
    df2 = pd.read_csv('../recomendacao_sys/df2.csv')
    df = pd.read_csv('../recomendacao_sys/df.csv')
    return df2, df


# Função para calcular a matriz de similaridade com o sistema do Jupyter
def calculate_similarity(df):
    """
    Calcula a similaridade entre os veículos utilizando as características dos veículos.
    Combina várias colunas de atributos para criar uma string única para cada veículo,
    e então calcula a similaridade entre essas representações usando CountVectorizer e Similaridade por Cosseno.
    """
    # Combinar os atributos relevantes em uma única string para cada veículo
    df['features'] = df[['modelo', 'preco', 'marca', 'km', 'ano', 'tipo',
                         'pot_motor', 'kit_gnv', 'cor', 'combustivel', 'portas',
                         'cambio', 'direcao', 'municipio']].apply(
        lambda x: ' '.join(map(lambda v: str(v) if v is not None else 'desconhecido', x)), axis=1
    )
    
    # Vetorização usando CountVectorizer
    vectorizer = CountVectorizer()
    vectorized = vectorizer.fit_transform(df['features'])
    
    # Calcular similaridade por cosseno
    similarities = cosine_similarity(vectorized)
    
    # Criar DataFrame de similaridade
    similarity_df = pd.DataFrame(similarities, columns=df['titulo'], index=df['titulo'])
    return similarity_df

# Função para obter recomendações
def get_recommendations(input_car, similarity_df, df, num_recommendations=5):
    """
    Gera uma lista de recomendações de veículos semelhantes com base na similaridade calculada.
    Exclui o próprio carro selecionado das recomendações e retorna as informações dos veículos recomendados.
    """
    # Buscar os carros mais semelhantes
    recommendations = similarity_df.nlargest(num_recommendations + 1, input_car)[input_car].index
    recommendations = [car for car in recommendations if car != input_car]  # Remove o carro selecionado
    
    # Juntar com o DataFrame original para exibir mais detalhes
    recommended_cars = df[df['titulo'].isin(recommendations)][['titulo', 'preco', 'marca', 'km', 'ano', 'url']]
    return recommended_cars

# Configuração do Streamlit
st.set_page_config(page_title="Recomendação de Veículos", page_icon="🚗", layout="wide")
st.title("🚗 Sistema de Recomendação de Veículos")
st.write("Descubra os veículos mais parecidos com suas escolhas. Selecione um carro para começar!")

# Adicionando uma barra lateral para navegação
st.sidebar.title("🔧 Configurações")
st.sidebar.write("Ajuste os parâmetros da recomendação ou veja informações adicionais.")

# Carregar dados do banco de dados
with st.spinner("Carregando dados do banco de dados..."):
    df2, df = load_data()
st.sidebar.success("Dados carregados com sucesso!")

# Mostrar algumas estatísticas básicas no topo
st.markdown("### 📊 Estatísticas dos Veículos")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total de Veículos", value=len(df))  # Exibe o total de veículos
with col2:
    st.metric(label="Preço Médio (R$)", value=f"{df['preco'].mean():,.2f}")  # Exibe o preço médio
with col3:
    st.metric(label="Ano Médio", value=int(df['ano'].mean()))  # Exibe o ano médio

# Calcular matriz de similaridade
with st.spinner("Calculando similaridade entre os veículos..."):
    similarity_df = calculate_similarity(df)  # Calcula a similaridade entre os veículos
st.sidebar.success("Similaridade calculada!")

# Seleção do carro
st.markdown("### 🚘 Escolha um veículo")
car_selected = st.selectbox("Escolha um anúncio pelo título:", df['titulo'])  # O usuário escolhe um veículo

# Botão para gerar recomendações
if st.button("🔍 Gerar Recomendações"):
    with st.spinner("Gerando recomendações..."):
        recommendations = get_recommendations(car_selected, similarity_df, df)  # Gera recomendações baseadas na seleção
    
    # Exibe as recomendações ou uma mensagem caso não haja
    if recommendations.empty:
        st.warning(f"Não há recomendações disponíveis para o veículo '{car_selected}'.")
    else:
        st.markdown(f"### 📋 Recomendações para **{car_selected}**")
        for _, row in recommendations.iterrows():
            with st.expander(row['titulo']):  # Exibe cada veículo recomendado
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Preço:** R$ {row['preco']:,.2f}")
                    st.write(f"**Marca:** {row['marca']}")
                    st.write(f"**Ano:** {row['ano']}")
                    st.write(f"**Quilometragem:** {row['km']} km")
                st.markdown(f"[🔗 Link para o anúncio]({row['url']})")
else:
    st.info("Clique no botão acima para gerar recomendações.")  # Instrução quando o botão ainda não foi clicado

# Rodar o Streamlit:
# Salve este código em um arquivo (exemplo: app.py) e execute:
# streamlit run app.py
