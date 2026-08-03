{{/*
SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
SPDX-License-Identifier: AGPL-3.0-or-later
*/}}

{{- define "traffic-a22-data-quality.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "traffic-a22-data-quality.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
