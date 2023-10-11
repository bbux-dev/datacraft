ip/ipv4
-------

Ip addresses can be generated
using `CIDR notation <https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing>`_
or by specifying a base. For example, if you wanted to generate ips in the
10.0.0.0 to 10.0.0.255 range, you could either specify a ``cidr`` param of
10.0.0.0/24 or a ``base`` param of 10.0.0.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "ipv4",
        "config": {
          "cidr": "<cidr value /8 /16 /24 only>",
          OR
          "base": "<beginning of ip i.e. 10.0>"
        }
      }
    }

Examples:

.. code-block:: json

    {
      "network": {
        "type": "ipv4",
        "config": {
          "cidr": "2.22.222.0/16"
        }
      },
      "network_shorthand:ip?cidr=2.22.222.0/16": {},
      "network_with_base:ip?base=192.168.0": {}
    }

ip.precise
----------

The default ip type only supports cidr masks of /8 /16 and /24. If you want more precise ip ranges you need to use the
``ip.precise`` type. This type requires a cidr as the single config param. The default mode for ``ip.precise`` is to
increment the ip addresses. Set config param sample to one of true, on, or yes to enable random ip addresses selected
from the generated ranges.

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "ip.precise",
        "config": {
          "cidr": "<valid cidr value>",
        }
      }
    }

Examples:

.. code-block:: json

    {
      "network": {
        "type": "ip.precise",
        "config": {
          "cidr": "192.168.0.0/14",
          "sample": "true"
        }
      }
    }

net.mac
-------

For creating MAC addresses

Prototype:

.. code-block:: python

    {
      "<field name>": {
        "type": "net.mac",
        "config": {
          "dashes": "If dashes should be used as the separator one of on, yes, 'true', or True"
        }
      }
    }

Examples:

.. code-block:: json

    {
      "network": {
        "type": "net.mac"
      }
    }

.. code-block:: json

    {
      "network": {
        "type": "net.mac",
        "config": {
          "dashes": "true"
        }
      }
    }