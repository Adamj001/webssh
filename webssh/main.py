import logging
import tornado.web
import tornado.ioloop

from tornado.options import options
from webssh import handler
from webssh.handler import IndexHandler, WsockHandler, NotFoundHandler
from webssh.settings import (
    get_app_settings, get_host_keys_settings, get_policy_setting,
    get_ssl_context, get_server_settings, check_encoding_setting
)


def make_handlers(loop, options):
    host_keys_settings = get_host_keys_settings(options)
    policy = get_policy_setting(options, host_keys_settings)

    handlers = [
        (r'/', IndexHandler, dict(loop=loop, policy=policy,
                                  host_keys_settings=host_keys_settings)),
        (r'/ws', WsockHandler, dict(loop=loop))
    ]
    return handlers


def make_app(handlers, settings):
    # 添加 WebSocket 心跳配置
    settings.update(
        default_handler_class=NotFoundHandler,
        websocket_ping_interval=30,  # 每 30 秒发送一次 ping
        websocket_ping_timeout=120   # 如果 120 秒内未收到 pong，则关闭连接
    )
    app = tornado.web.Application(handlers, **settings)
    return app


def app_listen(app, port, address, server_settings):
    app.listen(port, address, **server_settings)
    if not server_settings.get('ssl_options'):
        server_type = 'http'
    else:
        server_type = 'https'
        handler.redirecting = True if options.redirect else False
    logging.info(
        'Listening on {}:{} ({})'.format(address, port, server_type)
    )


def main():
    options.parse_command_line()
    check_encoding_setting(options.encoding)
    loop = tornado.ioloop.IOLoop.current()
    
    # 获取应用设置并记录日志
    app_settings = get_app_settings(options)
    logging.info(f"App settings: {app_settings}")
    
    app = make_app(make_handlers(loop, options), app_settings)
    ssl_ctx = get_ssl_context(options)
    server_settings = get_server_settings(options)
    
    # 记录服务器设置
    logging.info(f"Server settings: {server_settings}")
    
    app_listen(app, options.port, options.address, server_settings)
    if ssl_ctx:
        server_settings.update(ssl_options=ssl_ctx)
        app_listen(app, options.sslport, options.ssladdress, server_settings)
    
    logging.info("Starting IOLoop...")
    loop.start()


if __name__ == "__main__":
    main()
