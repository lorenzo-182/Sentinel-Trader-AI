
import pandas as pd
import matplotlib.pyplot as plt
def graficar_historial():
    # 1. Leer el archivo que generó tu bot
    if not pd.io.common.file_exists("historial_trading.csv"):
        print("No hay historial para graficar.")
        return

    df = pd.read_csv("historial_trading.csv")
    
    # 2. Filtrar solo un activo para que el gráfico sea claro (ej: S&P 500)
    df_sp500 = df[df['Activo'] == '^GSPC']

    # 3. Crear el gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(df_sp500['Fecha'], df_sp500['Precio'], marker='o', label='Precio S&P 500')
    
    # Resaltar las compras
    compras = df_sp500[df_sp500['Estado'] == 'COMPRA (Alcista)']
    plt.scatter(compras['Fecha'], compras['Precio'], color='green', s=100, label='Señal de Compra')

    plt.title('Rendimiento del Bot de Trading - S&P 500')
    plt.xlabel('Fecha')
    plt.ylabel('Precio (USD)')
    plt.legend()
    plt.grid(True)
    
    # Guardar la imagen para el video de YouTube
    plt.savefig('grafico_rendimiento.png')
    plt.show()

if __name__ == "__main__":
    graficar_historial()