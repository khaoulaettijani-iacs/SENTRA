
# ADR-002— Désactivation de X-Pack Security (ELK)

## Contexte

Dans l’architecture SENTRA, la stack ELK (Elasticsearch, Kibana, Logstash) est déployée via Docker Compose sur la VM SOC.

Configuration actuelle :
```yaml
xpack.security.enabled=false
````
Par défaut, Elasticsearch 8.x active :
* authentification (users / passwords)
* TLS
* contrôle d’accès

Cependant, ces mécanismes ont été volontairement désactivés dans ce lab.

Activer X-Pack implique :

* gestion des certificats TLS
* gestion des utilisateurs et rôles
* configuration Kibana + Logstash sécurisée

Cela ajoute une complexité importante pour un environnement de prototype.

Nous acceptons de désactiver la sécurité X-Pack car l’environnement est fortement isolé :

```yaml
xpack.security.enabled=false
```

### 1. Réseau Docker interne

* Les services ELK communiquent via `soc-net`
* Réseau **non exposé directement à l’extérieur**

### 2. Segmentation réseau (pfSense)

* La VM SOC est située sur **VMnet4 (192.168.30.0/24)**
* Isolation stricte :

  *  Aucun accès direct depuis Kali (attaquant)
  * Seuls flux nécessaires autorisés (ex: Filebeat → Logstash)

### 3. Environnement de lab

* Pas de données sensibles réelles



---

##  Alternative en production

En environnement réel, il faut :

* activer `xpack.security.enabled=true`
* configurer TLS (HTTPS)
* gérer utilisateurs / rôles
* restreindre l’accès réseau (firewall + reverse proxy)

---

##  Conséquences

### Avantages

* simplicité de déploiement
* gain de temps
* moins d’erreurs de configuration

### Inconvénients

* absence de sécurité native ELK
* dépendance totale à la segmentation réseau

---

## Conclusion

La désactivation de X-Pack est un **compromis** acceptable dans SENTRA grâce à :

* isolation réseau (pfSense)
* réseau Docker interne
* absence d’exposition externe