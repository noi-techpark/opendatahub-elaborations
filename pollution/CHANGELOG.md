# Changelog

[[_TOC_]]

## Version 0.*

### 0.1.1

:rocket: New features:
* Updated pollution computation model, now the km data is loaded from station metadata
* Improved task execution time by:
  * Added smarter logic for computing the starting date for a station batch
  * Added computation checkpoints

### 0.1.0

:rocket: New features:
* Added data model for traffic and pollution measure.
* Added celery worker and scheduler.
* Added a connector for ODH traffic data.
* Implemented the pollution computation task.
* Implemented the pollution computation model.
* Added a connector for ODH pollution data.

:house: Internal:
* Added sentry integration.

###
