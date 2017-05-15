from core import server, messaging, misc

s = server.Server(misc.create_resources, '/tmp')
s.start()
m = messaging.Messanger(s.queue)
engine, session = m.wait_for_resource()
pass