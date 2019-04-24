MACS = ['5c:70:a3:0e:28:b2', '04:d6:aa:69:da:f1']     #estas serian las MACs usadas para entrenar el modelo

Classes = ['Sillon1', 'PasilloDerecha', 'PasilloIzquierda', 'Sillon2']  # estas son las zonas en las cuales quiero que el modelo aprenda que los celulares van

test_times = [('20190411-115300', '20190411-120000'), ('20190411-120400','20190411-121200'),
                  ('20190411-121400', '20190411-122300'), ('20190411-125700','20190411-130700')]  # rangos de tiempo en los que se realizo cada entrenamiento, uno por cada clase

train_data_path = "/home/ubuntu/webserver/logs/"

