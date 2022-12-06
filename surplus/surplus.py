import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Parâmetros

area = 4317 # original: 4317
delta = 0.10 # percentual do consumo [%]

# Dados do consumo

dados_consumo=pd.read_csv("dados_consumo.csv", sep=";", header=None)
dados_consumo.rename({0:'Date',
           1:'Month',
           2:'Cons'},axis=1,inplace=True)

dados_consumo.index=pd.to_datetime(dados_consumo['Date'])
dados_consumo.drop('Date',axis=1,inplace=True)
dados_consumo.drop('Month',axis=1,inplace=True)
dados_consumo['Cons']=dados_consumo['Cons'].str.replace(',','.')
dados_consumo['Cons']=dados_consumo['Cons'].astype(float)
dados_consumo=dados_consumo.resample('1h').sum()
dados_consumo['Cons']=dados_consumo['Cons'].resample('1h').sum()

dados_consumo.loc[dados_consumo.index=='2018-02-28','Cons'] = dados_consumo['Cons'].mean() # outlier

# Leitura e tratamento dos dados

dados_irradiacao=pd.read_csv("dados_irradiacao.csv", sep=";")
dados_irradiacao['Irradiacao']=dados_irradiacao['Irradiacao'].str.replace(',','.').astype(float)

# Função que calcular a energia gerada por PV

def PV_out(dados_irradiacao):
    dados_irradiacao['PV_Out']=dados_irradiacao['Irradiacao']*0.15*0.95*area
    return dados_irradiacao

PV_out(dados_irradiacao)
dados_irradiacao['PV_Out'].plot()

plt.gcf().set_size_inches(15, 8) # tamanho da figura
plt.xlabel("Days")
plt.ylabel("Irradiation [kWh]",fontsize='large')

for i,row in dados_consumo.iterrows():
    dados_consumo.loc[i,'Irradiacao']=dados_irradiacao.loc[(dados_irradiacao.hora==i.hour) & (dados_irradiacao.mês==dados_irradiacao['mês'].unique()[i.month-1]),'Irradiacao'].values[0]
dados_consumo = PV_out(dados_consumo)

# Definindo o surplus de energia

dados_consumo['Cons'] = dados_consumo['Cons']*delta # variando delta, conseguimos 'brincar' com valor do consumo
dados_consumo['Surplus'] = dados_consumo['PV_Out'] - dados_consumo['Cons']

# Gráficos do surplus

plt.figure(figsize=(30, 30))
plt.subplots_adjust(hspace=0.25)
plt.suptitle("Surplus per month", fontsize=30, y=0.91)

for n, i in enumerate(range(1,13)):
    ax = plt.subplot(6, 2, n + 1)
    dados_consumo[['PV_Out','Cons','Surplus']].loc[(dados_consumo.index.month==i)].plot(ax=ax, label="PV Output")
    plt.legend(loc="upper left")
    plt.ylabel("Energy [MWh]")

# plot de um mês -> mudar index.month == ' '
dados_consumo[['PV_Out','Cons','Surplus']].loc[(dados_consumo.index.month==8)].plot()
plt.gcf().set_size_inches(15, 8) # tamanho da figura

# legenda do gráfico
pv_out = mpatches.Patch(facecolor='#0000FF', label='PV Output', linewidth = 0.5, edgecolor = 'black')
cons = mpatches.Patch(facecolor='#ff9700', label = 'Consumption', linewidth = 0.5, edgecolor = 'black')
surplus = mpatches.Patch(facecolor='#00FF00', label = 'Surplus', linewidth = 0.5, edgecolor = 'black')
legend = plt.legend(handles=[pv_out,cons,surplus], loc=4, fontsize='large', fancybox=True)

# labels
plt.ylabel("Energy [MWh]",fontsize='large')

# Média mensal de surplus

for i in range(1,13):
    print(i, ":", dados_consumo['Surplus'].loc[(dados_consumo.index.month==i)].mean())

dados_consumo.to_csv('dados.csv')
