# Hetzner DynDNS Bridge

This is a super simple HTTP Service that translates DynDNS update requests (like those that are supported by all FRITZ!Box Models) into a series of Hetzner DNS Console API requests so you can effectively use Hetzner as a DynDNS provider.

## Configuration

The service itself does not use store any API keys, but gets the API Key from the query parameters in the request from the FRITZ!Box, so TLS termination of the service is a good idea.

Configure your FRITZ!Box DynDNS Settings (Internet -> Shares -> DynDNS) like this:

- Provider: `Custom`
- Update URL: `https://<Your Service Address>/update?domain=<domain>&auth_key=<passwd>&ip4=<ipaddr>`
- Domainname: *whatever you DNS enrty you want to update*
- Username: *does not matter but you need to enter something*
- Password: *your hetzner API key*

For creating AAAA records (IPv6) use the following URL
Update URL: `https://<Your Service Address>/update?domain=<domain>&auth_key=<passwd>&ip4=<ipaddr>&ip6=<ip6addr>`

## Deployment

The most simple deployment usecase is with the included `docker-compose.yml`. This assumes a traefik deployment with a docker provider somewhere on the running server. You can also remove the `label` and `networks` definitions and expose the port 80 directly or just run the service without Docker alltogether by running `poetry install && poetry run python -m hetzner_ddns`

## Why not X

There are many other projects and tutorials that aim to solve a very similar usecase. This is my attempt mostly because I could and I had fun making it. Some things that are different from other approaches:

- No storing of API Keys in the service, the Hetzner API Key is only stored in the FRITZ!Box
- No polling of your IP Address. Your router knows best when th IP changes and only then updates the entries
