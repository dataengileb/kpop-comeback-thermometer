# Termómetro de comebacks

[English](README.md) · **Español**

¿Qué tan fuerte es cada nuevo lanzamiento de TWICE, NMIXX o tripleS al día 1, 7 y 28, comparado con los lanzamientos anteriores del mismo artista en el mismo mercado? Los artistas incluyen sus unidades y solistas. YouTube solo muestra totales históricos, que siempre favorecen a los éxitos viejos, así que este proyecto toma una foto diaria de los contadores.

**Sitio:** [dataengileb.github.io/kpop-comeback-thermometer](https://dataengileb.github.io/kpop-comeback-thermometer/?lang=es) · **Alcance:** [RFP](docs/rfp.md) y [SOW](docs/sow.md) · **Artistas y canales:** [`artists.json`](src/config/artists.json) · **Agregar artistas o métricas:** [extending.md](docs/extending.md)

## Cómo funciona

1. Todos los días a las 07:00, hora de la Ciudad de México, Step Functions corre tres Lambdas que guardan en S3 una foto de YouTube, Last.fm y MusicBrainz. Las respuestas crudas quedan intactas en bronze. Los registros que cumplen su [contrato](src/contracts) van a silver y el resto a cuarentena, y si más del 5% lo rompe, la corrida se detiene.
2. Athena reconstruye dos tablas gold Iceberg con `MERGE` y corre pruebas de datos ([ADR 4](docs/adr/0004-gold-iceberg-tables-rebuilt-with-merge.md)).
3. Una Lambda exporta gold a un archivo JSON fechado, que es lo que lee el sitio estático. El sitio nunca se conecta a AWS.

![Arquitectura: EventBridge Scheduler inicia Step Functions cada día. Step Functions encabeza un recuadro con todos los servicios que llama, numerados en el orden de la corrida. Corre tres Lambdas de ingesta en paralelo, que leen las llaves de API de SSM, consultan YouTube, Last.fm y MusicBrainz, y escriben en S3. Después Athena hace MERGE de silver en dos tablas Iceberg gold a través del catálogo de Glue, las revisa y las compacta con VACUUM. La Lambda export_site lee gold y escribe en S3 un corte fechado en JSON; fetch_export.sh lo copia a site/data/ y publish_site.sh publica el sitio en GitHub Pages, que nunca llama a AWS. Las fallas de la corrida o de las revisiones llegan por correo vía SNS, y AWS Budgets avisa desde el primer centavo.](docs/architecture.png)

Dibujado con [Diagramon](https://github.com/dataengileb/diagramon) a partir de [su fuente](docs/architecture.diagramon.txt). El cian marca el flujo principal de datos y el rosa, las alertas. Las capas de datos y el orden de los pasos tienen sus propios diagramas en [diagrams.md](docs/diagrams.md) (en inglés).

Es la modernización de [mi versión de 2023](https://github.com/Proggleb/youtube_data_engineering_project) (EC2 + RDS + Tableau). Por qué cambió: [ADR 1](docs/adr/0001-serverless-batch-instead-of-ec2-rds.md).

## Lo que sí es y lo que no

- Mide atención en YouTube y Last.fm, no ventas, posiciones en charts ni streams en otras plataformas.
- Los valores al día N solo existen para videos publicados después de la primera foto. Los comebacks anteriores se muestran, pero no se comparan.
- Cada lanzamiento se compara solo con los del mismo artista para el mismo mercado (Corea o Japón): un MV japonés o un debut en solitario no se mide contra un sencillo principal de TWICE.
- Los usuarios de Last.fm son sobre todo occidentales, y Last.fm se omite para las unidades de tripleS porque acredita sus reproducciones a tripleS.
- Solo incluye artistas con un MV oficial en los canales de `artists.json`.
- Guarda estadísticas de YouTube más allá de los 30 días que permiten sus políticas, y las compara entre sí. Se acepta en este proyecto académico sin fines comerciales, no para un cliente comercial ([riesgo](docs/sow.md#6-risks)).

## Cómo correrlo

Necesitas una cuenta de AWS, el AWS CLI y Python 3.14. Las llaves y el stack deben estar en la misma región (`us-east-1`, salvo que definas `AWS_REGION`). El costo es de unos USD 0.01 al mes, todo de Athena, cubierto por los créditos del free tier: cero gasto de bolsillo. Una alerta de presupuesto, neta de créditos, te avisa desde el primer centavo gastado.

```bash
read -rs KEY && aws ssm put-parameter --region us-east-1 --type SecureString --name /comeback-thermometer/youtube-api-key --value "$KEY"
read -rs KEY && aws ssm put-parameter --region us-east-1 --type SecureString --name /comeback-thermometer/lastfm-api-key --value "$KEY"
unset KEY
ALERT_EMAIL=tu@correo.com ./scripts/deploy.sh
```

Confirma el correo de SNS. La primera corrida ocurre a las 07:00 siguientes, o lánzala a mano con `aws stepfunctions start-execution --state-machine-arn <PipelineArn>`. Para actualizar el sitio, corre `./scripts/fetch_export.sh`, haz commit de `site/data/` y luego corre `./scripts/publish_site.sh`. El sitio se actualiza cada lunes, y a diario durante la primera semana de un lanzamiento, así que su fecha de datos nunca tiene más de una semana.

Pruebas: `pip install -r requirements-dev.txt && pytest && cfn-lint`.
