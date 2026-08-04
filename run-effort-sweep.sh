#!/bin/bash
# Effort sweep, pre-registered: 5 levels x (6 hard oracle x 3 trials + 13 blind event-bus)
set -u
HARD="13-order-totals,14-event-bus,15-csv-import,16-task-scheduler,17-json-patch,18-pagination-sync"
for E in low medium high xhigh max; do
  echo ""
  echo "############ EFFORT=$E — hard oracle (6 tasks x 3 trials) ############"
  node --env-file=.env src/run.ts --models claude-opus-5 --tasks "$HARD" --trials 3 --concurrency 4 --effort "$E"
  echo ""
  echo "############ EFFORT=$E — blind event-bus (13 trials) ############"
  node --env-file=.env src/run.ts --models claude-opus-5 --tasks 14-event-bus --trials 13 --blind --concurrency 4 --effort "$E"
done
echo ""
echo "############ SWEEP COMPLETE ############"
