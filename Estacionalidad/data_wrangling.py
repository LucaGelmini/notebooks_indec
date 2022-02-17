import pandas as pd
from collections import Counter


def data_wrangling():

    #input paths
    serie_mensual = './Datos/serie_mensual_indices_comex.xls'
    intercambio_comercial = "./Datos/Serie Intercambio comercial.csv"
    indice_terminos_intercambio = './Datos/ITI(B04)_mensual.xlsx'
    indice_flete = './Datos/Estacionalidad flete.xlsx'

    #dominio de la serie
    desde = 2011
    hasta = 2021

    ########################   Cargamos las tablas    ##########################
    df_serieMensual = pd.read_excel(serie_mensual, header=None, skiprows = 5, index_col=None)

    ### Loop the data lines
    with open(intercambio_comercial, 'r') as temp_f:
        # get No of columns in each line
        col_count = [ len(l.split(",")) for l in temp_f.readlines() ]
    ### Generate column names  (names will be 0, 1, 2, ..., maximum columns - 1)
    column_names = ['Año', 'Mes', 'v_expo', 'v_impo','Intercambio_comercial']
    ### Read csv
    df_icomercial = pd.read_csv(intercambio_comercial, header=None, delimiter=";", names=column_names, skiprows = 1, index_col=None)

    df_iti = pd.read_excel(indice_terminos_intercambio, index_col=None)


    df_serieMensual= df_serieMensual.rename(columns = {0:'Año', 1: 'Mes', 2:'iv_x', 3:'ip_x', 4:'iq_x', 5:'del',6:'iv_m',7:'ip_m',8:'iq_m'})
    df_serieMensual = df_serieMensual.drop(columns="del")
    df_serieMensual = df_serieMensual[df_serieMensual['Mes'].notna()]



    ############################   Wrangling serie mensual   ###############################

    # paso Mes a las primeras tres letras y en lowercase
    df_serieMensual['Mes'] = list(map(lambda m: m[:3].lower(), df_serieMensual.Mes))
    # hacemos que cada fila diga su año, no solo los eneros
    def completa_con_anios(df_anios):
        anios = []
        arranque = int(df_anios[0])
        for i in range(len(df_anios)):
            if ((i % 12 == 0) and (i != 0)):       
                arranque+=1
                anios.append(arranque)
            else:
                anios.append(arranque)
        return anios

    df_serieMensual['Año'] = completa_con_anios(df_serieMensual.Año)


    #Enumeramos los meses y los agregamos como columna al df
    def enumera_meses(df_mes):
        nombre_meses = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
        return [nombre_meses.index(i)+1 for i in df_mes]

    df_serieMensual['Mes_num'] = enumera_meses(df_serieMensual.Mes)


    #Agregamos columnas con la variacion interanual

    def var_inter(df, col_name: str):
        return df[col_name].pct_change(periods=12, fill_method='bfill')

    df_serieMensual['iv_x_var']= var_inter(df_serieMensual, 'iv_x')
    df_serieMensual['ip_x_var']= var_inter(df_serieMensual, 'ip_x')
    df_serieMensual['iq_x_var']= var_inter(df_serieMensual, 'iq_x')
    df_serieMensual['iv_m_var']= var_inter(df_serieMensual, 'iv_m')
    df_serieMensual['ip_m_var']= var_inter(df_serieMensual, 'ip_m')
    df_serieMensual['iq_m_var']= var_inter(df_serieMensual, 'iq_m')

    #Ordenamos el df con estacionalidad
    df_serieMensual = df_serieMensual.sort_values(['Mes_num', 'Año'])

    #seleccionamos el dominio de la serie del df
    df_serieMensual = df_serieMensual.loc[(df_serieMensual['Año'] >= desde) & (df_serieMensual['Año'] <= hasta)]
    df_serieMensual.reset_index(drop=True, inplace=True)

    # Hacemos un df provisorio con las medias
    medias = df_serieMensual.groupby(['Mes_num']).mean()

    def repite_medias(df_target, media_col):
        media = []
        muestras_x_mes = Counter(df_target.Mes)
        for i, valor in enumerate(media_col):
            for _ in range(list(muestras_x_mes.values())[i]):
                media.append(valor)
        return media

        

    print(medias)
    df_serieMensual['iv_x_media'] = repite_medias(df_serieMensual, medias.iv_x)
    df_serieMensual['iv_m_media'] = repite_medias(df_serieMensual, medias.iv_m)
    df_serieMensual['ip_x_media'] = repite_medias(df_serieMensual, medias.ip_x)
    df_serieMensual['ip_m_media'] = repite_medias(df_serieMensual, medias.ip_m)
    df_serieMensual['iq_x_media'] = repite_medias(df_serieMensual, medias.iq_x)
    df_serieMensual['iq_m_media'] = repite_medias(df_serieMensual, medias.iq_m)


    del medias



    ################################# Wrangling de Intercambio Comercial #############################

    df_icomercial.v_expo = [x.replace(',', '.') for x in df_icomercial.v_expo]
    df_icomercial.v_impo = [x.replace(',', '.') for x in df_icomercial.v_impo]
    df_icomercial.Intercambio_comercial = [x.replace(',', '.') for x in df_icomercial.Intercambio_comercial]

    df_icomercial.v_expo = df_icomercial.v_expo.astype(float)
    df_icomercial.v_impo = df_icomercial.v_impo.astype(float)
    df_icomercial.Intercambio_comercial = df_icomercial.Intercambio_comercial.astype(float)

    df_icomercial = df_icomercial.rename(columns={'Intercambio_comercial': 'i_com'})
    
    df_icomercial['v_expo_var']= var_inter(df_icomercial, 'v_expo')
    df_icomercial['v_impo_var']= var_inter(df_icomercial, 'v_impo')
    df_icomercial['i_com_var']= var_inter(df_icomercial, 'i_com')

    #divido los valores por un millon porque nos manejamos por millones de dolares
    df_icomercial.v_expo = [x/1000000 for x in df_icomercial.v_expo]
    df_icomercial.v_impo = [x/1000000  for x in df_icomercial.v_impo]
    df_icomercial.i_com = [x/1000000  for x in df_icomercial.i_com]

    #Orden estacional
    df_icomercial=df_icomercial.sort_values(['Mes', 'Año'])

    #seleccionamos el dominio de la serie del df
    df_icomercial = df_icomercial.loc[(df_icomercial.Año >= desde)&(df_icomercial.Año <= hasta)]
    df_icomercial.reset_index(drop=True, inplace=True)

    #df de medias
    medias = df_icomercial.groupby(['Mes']).mean()

    df_icomercial['v_expo_media'] = repite_medias(df_icomercial, medias.v_expo)
    df_icomercial['v_impo_media'] = repite_medias(df_icomercial, medias.v_impo)
    df_icomercial['i_com_media'] = repite_medias(df_icomercial, medias.i_com)

    del medias



    ####################################### Wrangling ITI #####################################
    df_iti = pd.read_excel(indice_terminos_intercambio)

    df_iti['Año'] = [fecha.year for fecha in df_iti.Período]
    df_iti['Mes'] = [fecha.month for fecha in df_iti.Período]
    del df_iti['Período']
    df_iti['ITI_var'] = df_iti.ITI.pct_change(periods=12, fill_method='bfill')

    #Orden estacional
    df_iti=df_iti.sort_values(['Mes', 'Año'])
    df_iti

    #Filtro
    df_iti= df_iti.loc[(df_iti['Año'] >= desde)&(df_iti['Año'] <= hasta)]
    df_iti.reset_index(drop=True, inplace=True)
    
    #Calculo medias
    medias = df_iti.groupby(['Mes']).mean()
    #agrego las medias a df
    df_iti['ITI_media'] = repite_medias(df_iti, medias.ITI)

    del medias



    ################################# Wrangling flete #################################
    df_flete = pd.read_excel(indice_flete)
    df_flete.ip_flete_var = list(map(lambda x: x/100, df_flete.ip_flete_var))
    df_flete= df_flete.loc[(df_flete['Año'] >= desde)&(df_flete['Año'] <= hasta)]
    df_flete.reset_index(drop=True, inplace=True)



    ################################ Unión #########################################

    #Dejamos el año y el mes solo para la primer tabla
    del df_iti['Año']
    del df_iti['Mes']
    del df_icomercial['Año']
    del df_icomercial['Mes']
    del df_flete['Año']
    del df_flete['Mes']

    df_estacional = pd.concat([df_serieMensual, df_icomercial, df_iti,df_flete], axis=1)

    #reordeno las columnas
    df_estacional = df_estacional[['Año', 'Mes', 'Mes_num', 'iv_x', 'ip_x', 'iq_x', 'iv_m', 'ip_m', 'iq_m', 
       'iv_x_var', 'ip_x_var', 'iq_x_var', 'iv_m_var', 'ip_m_var', 'iq_m_var',
       'iv_x_media', 'iv_m_media', 'ip_x_media', 'ip_m_media', 'iq_x_media', 'iq_m_media',
       'v_expo', 'v_impo', 'i_com', 'v_expo_var', 'v_impo_var', 'i_com_var',
       'v_expo_media', 'v_impo_media', 'i_com_media', 'ITI', 'ITI_var', 'ITI_media','ip_flete','ip_flete_var','ip_flete_media']]


    
    return df_estacional