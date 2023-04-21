# Configuring Rate Limiting

The benefits application has a simple, single-configuration Rate Limit that acts
per-IP to limit the number of consecutive requests in a given time period, via
nginx [`limit_req_zone`](http://nginx.org/en/docs/http/ngx_http_limit_req_module.html#limit_req_zone)
and [`limit_req`](http://nginx.org/en/docs/http/ngx_http_limit_req_module.html#limit_req) directives.

The configured rate limit is 12 requests/minute, or 1 request/5 seconds:

```nginx
limit_req_zone $limit zone=rate_limit:10m rate=12r/m;
```

## HTTP method selection

An NGINX [map](http://nginx.org/en/docs/http/ngx_http_map_module.html#map)
variable lists HTTP methods that will be rate limited:

```nginx
map $request_method $limit {
    default         "";
    POST            $binary_remote_addr;
}
```

The `default` means don't apply a rate limit.

To add a new method, add a new line:

```nginx
map $request_method $limit {
    default         "";
    OPTIONS         $binary_remote_addr;
    POST            $binary_remote_addr;
}
```

## App path selection

The `limit_req` is applied to an NGINX [`location`](https://nginx.org/en/docs/http/ngx_http_core_module.html#location) block with a case-insensitive regex to match paths:

```nginx
location ~* ^/(eligibility/confirm)$ {
    limit_req zone=rate_limit;
    # config...
}
```

To add a new path, add a regex OR `|` with the new path (omitting the leading slash):

```nginx
location ~* ^/(eligibility/confirm|new/path)$ {
    limit_req zone=rate_limit;
    # config...
}
```
