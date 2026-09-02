# Bento Beacon

This is an implementation of the [GA4GH Beacon v2 standard](https://www.ga4gh.org/product/beacon-api/) for genomic data discovery for the [Bento platform](https://bento-platform.github.io/).

Beacon is a data-discovery tool that answers queries about genetic variation and clinical-phenotypic metadata. Its goal is to allow researchers to discover genomic and medical data worldwide without compromising dataset privacy or ownership. Bento beacon makes data stored in Bento discoverable in a secure and configurable manner.

_See a live bento beacon instance with synthetic data here_: [Bento GDI beacon](https://gdi.bento.sd4h.ca/en/beacon).

_See an instance of a network of bento beacons with four nodes here_: [Bento GDI beacon network](https://gdi.bento.sd4h.ca/en/network).

## Queries

Queries are accepted at `/individuals` and `/g_variants` using POST (later versions will support GET).

Full syntax of a beacon query is detailed in the beacon [documentation](https://docs.genomebeacons.org/variant-queries/). The different metadata filters available for use in each beacon are listed at each beacon's `/filtering_terms` endpoint.

## Responses

Beacon responses have different response _granularities_, giving a response that matches the user's permissions:

- **full record response**, typically given only to authorized users
- **count** or **boolean** responses, more appropriate for anonymous users, although can also require permissions if desired. These responses also have a configurable response threshold where very small count results are rounded to zero to avoid data leaks.

Where appropriate, bento beacons can also return aggregate responses to queries, giving e.g. a distribution of diseases in the dataset for a particular genetic variant.

Permissions are configured in the main Bento application, see [here](https://github.com/bento-platform/bento/blob/main/docs/installation.md#6-configure-permissions) for details.

The beacon endpoints `/biosamples`, `/runs` and `/analyses` are not yet implemented.

## Configuration

Configuration is done through the Bento application, see in particular the instructions [here](https://github.com/bento-platform/bento). The beacon can be accessed through a user interface on the [bento public](https://github.com/bento-platform/bento_public) portal, or run as a back-end only API.

## Beacon Network

Bento beacons can optionally be organized into a network, which allows users to query multiple beacons with a single query. Any bento beacon that permits anonymous queries returning count responses can be added to the network. An example network configuration file is [here](https://github.com/bento-platform/bento/blob/main/etc/templates/beacon/beacon_network_config.example.json).

## Resources

- [About Bento](https://bento-platform.github.io/)
- [Beacon v2 specification](https://github.com/ga4gh-beacon/beacon-v2)
- [Beacon v2 documentation](https://docs.genomebeacons.org/)
