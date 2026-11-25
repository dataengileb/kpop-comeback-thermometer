# Diagrams

Three views of the same pipeline, each drawn with [Diagramon](https://github.com/dataengileb/diagramon) from a text source. Each one answers a different question, so each one leaves something out. The source of truth is always the code: `infra/template.yaml` and `src/`.

| Diagram | Question it answers | For | What it leaves out |
|---|---|---|---|
| [Architecture](architecture.png) ([source](architecture.diagramon.txt)) | Which AWS services does it use, and where does each one run? | anyone reading the README: recruiters, the client, students | the order of the steps and the data layers |
| [Data flow](data-flow.png) ([source](data-flow.diagramon.txt)) | What happens to the data, layer by layer? | students, whoever checks data quality | who runs each step, IAM, alerts |
| [Daily run](pipeline.png) ([source](pipeline.diagramon.txt)) | In what order do the steps run, and where does a failure go? | whoever operates the pipeline or reads a failed execution | the storage and the external APIs |

The README shows only the architecture diagram.

## Data flow

![Data flow: the ingestion Lambdas pull from YouTube, Last.fm and MusicBrainz over HTTPS and check each record against its data contract. They write the untouched responses to bronze/, the records that pass to silver/ and the ones that fail to quarantine/, and more than 5% failures stops the run. Glue silver tables read silver/ in place, Athena MERGEs them into the gold/ Iceberg tables, and export_site reads gold and writes exports/. fetch_export.sh copies the export into site/data/ and publish_site.sh publishes it to GitHub Pages.](data-flow.png)

## Daily run

![Daily run of the Step Functions state machine Pipeline: EventBridge Scheduler starts it. A Parallel state runs the YouTube, Lastfm and MusicBrainz Lambdas, each retried twice. CheckSources goes to NotifyFailure if a source failed; otherwise BuildVideoLaunch and BuildArtistDaily MERGE the gold tables, CheckGold and ReadChecks run and read the data checks, and ChecksPassed goes to NotifyFailure if a check failed. Then VacuumVideoLaunch and VacuumArtistDaily expire old snapshots, ExportSite writes the site export and the run ends in Done. Any error in a step also goes to NotifyFailure, which emails through SNS and ends in Failed.](pipeline.png)

## Refreshing a diagram

Open the `.diagramon.json` file in Diagramon, change it (or paste the edited `.diagramon.txt` into the *Text* tab), then use **Export > PNG** and **Export > JSON**. Keep the `.txt` source in step with the JSON.
