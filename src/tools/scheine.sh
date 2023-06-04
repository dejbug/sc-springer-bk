#!/bin/bash
[ ! -a "scheine.json" ] && curl -skL -o scheine.json "https://scheinefuervereine.rewe.de/consumer-api/customer.php?action=get_club&id=10000037078";
[ -a "scheine.json" ] && sed -n 's/.*,"totalBalance":\([^,]*\).*/\1/p' scheine.json
