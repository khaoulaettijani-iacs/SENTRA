# Configuration syslog-ng (pfSense) pour l'export EVE JSON

Afin de contourner les limitations de taille du syslog FreeBSD, Suricata écrit dans `eve.json` et `syslog-ng` se charge de l'expédition TCP.

### Paramètres des Objets syslog-ng 

**1. Source (`src_suricata`)**
\`\`\`text
source src_suricata {
  wildcard-file(
    base-dir("/var/log/suricata")
    filename-pattern("eve.json")
    recursive(yes)
    follow-freq(1)
    program-override("suricata")
    flags(no-parse)
  );
};
\`\`\`

**2. Destination (`dst_logstash`)**
\`\`\`text
destination dst_logstash {
  network(
    "192.168.30.10"
    port(5000)
    transport("tcp")
    template("$MSG\n") # Envoi du JSON pur
  );
};
\`\`\`

**3. Log Path**
Relier `src_suricata` à `dst_logstash`.