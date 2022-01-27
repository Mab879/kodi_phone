import ari
import kodijson
import sys
import os

client = ari.connect('http://10.0.0.45:8088', 'kodi', os.envrio.get('ARI_PASSWORD'))
kodi = kodijson.Kodi("http://10.0.0.251:8080/jsonrpc", ("kodi"))

class g():
    pass

g.mode = 0

def on_start(incoming, event):
    print("Received call")
    incoming = incoming['channel']
    incoming.answer()

    def on_dtmf(channel, event):
        modes = [
                on_dtmf_root,
                on_dtmf_startrek,
                on_dtmf_season,
                on_dtmf_episode
        ]
        modes[g.mode](channel, event)
    
    def on_dtmf_root(channel, event):
        print("Received DTMF")
        digit = event['digit']
        print("Digit: " + digit)

        if digit == '*':
            kodi.Application.SetVolume(volume='decrement')
        elif digit == '#':
            kodi.Application.SetVolume(volume='increment')
        elif digit == '0':
            kodi.Player.PlayPause(playerid=1)
        elif digit == '9':
            print("Entering Star Trek Mode")
            g.mode = 1
        elif digit == '1':
            kodi.Input.Back()
        elif digit == '2':
            kodi.Input.Up()
        elif digit == '3':
            kodi.Input.Select()
        elif digit == '4':
            kodi.Input.Left()
        elif digit == '5':
            kodi.Input.Down()
        elif digit == '6':
            kodi.Input.Right()
        elif digit == '7':
            kodi.Input.ContextMenu()

    def on_dtmf_startrek(channel, event):
        print("Received DTMF for Star Trek")
        digit = event['digit']
        print("Digit: " + digit)

        shows = kodi.VideoLibrary.GetTVShows()['result']['tvshows']
        tng = [x for x in shows if 'The Next Generation' in x['label']][0]
        ent = [x for x in shows if 'Enterprise' in x['label']][0]

        print("TNG: " + str(tng['tvshowid']))
        print("ENT: " + str(ent['tvshowid']))

        if digit == '1':
            print("Selected TOS")
            g.mode = 2
        elif digit == '2':
            print("Selected TNG")
            g.show = tng['tvshowid']
            g.mode = 2
        elif digit == '3':
            print("Selected DS9")
            g.mode = 2
        elif digit == '4':
            print("Selected VOY")
            g.mode = 2
        elif digit == '5':
            print("Selected ENT")
            g.show = ent['tvshowid']
            g.mode = 2
        elif digit == '6':
            print("Selected DSC")
            g.mode = 2
        elif digit == '#':
            print("Exiting")
            g.mode = 0
        elif digit == '*':
            print("Going back")
            g.mode = 0

    def on_dtmf_season(channel, event):
        print("Received DTMF for Season Selection")
        digit = event['digit']
        print("Digit: " + digit)

        try:
            digit = int(digit)
            print("Selected season " + str(digit))
            g.season = digit
            g.episode = -1
            g.mode = 3
        except ValueError:
            if digit == '#':
                print("Exiting")
                g.mode = 0
            elif digit == '*':
                print("Going back")
                g.mode = 1

    def on_dtmf_episode(channel, event):
        print("Received DTMF for episode selection")
        digit = event['digit']
        print("Digit " + digit)

        try:
            digit = int(digit)
            if g.episode == -1:
                g.episode = digit
                print("Saved first digit " + str(g.episode))
            else:
                g.episode = (g.episode * 10) + digit
                print("Loading episode " + str(g.episode))
                g.mode = 0

                ep = kodi.VideoLibrary.GetEpisodes(
                        tvshowid=g.show,
                        season=g.season)
                ep = ep['result']['episodes']
                ep = [x for x in ep if ('x%02d' % g.episode) in x['label']][0]
                ep = ep['episodeid']
                print("Episode ID of selected episode " + str(ep))
                
                kodi.Player.Open(item={'episodeid':ep})
                g.mode = 0

        except ValueError:
            if digit == '#':
                print("Exiting")
                g.mode = 0
            elif digit == '*':
                print("Going back")
                g.mode = 1

    incoming.on_event('ChannelDtmfReceived', on_dtmf)

client.on_channel_event('StasisStart', on_start)
