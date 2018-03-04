<template>
  <div>
    <div style="position:relative" id="playerholder">
      <div id="player"></div>
      <video-overlay-panel v-if="show_overlay" :initialPlaybackRateIndex="current_playback_rate_index" @restartPlayback="playVideo" style="background: rgba(100,100,100, 0.01); position:absolute; top:0; left:0; width:100%;height:80%; z-index:1000;"></video-overlay-panel>
      <!--
      <button style="position:absolute; top:0; left:0; width:20;height:20;z-index:16777271;" @click="overlay=!overlay">C</button>
      //-->
    </div>
  </div>    
</template>
<script>
  import Vue from 'vue'

  export default {
    name: 'player-youtube',
    props: ['videoid'],
    data() {
      return { 
        player: null,
        done: false,
        show_overlay: false,
        playback_rates: [0.25, 0.5, 1, 1.25, 1.5, 2],
        current_playback_rate_index: 2
      }
    },
    methods: {
      getCurrentTime: function() {
        return this.player.getCurrentTime();
      },

      resizeVideo: function() {
        try {
          document.getElementById('player').width = document.getElementById('videoarea').clientWidth - 30;
          document.getElementById('player').height = document.getElementById('player').width * (9/16);
        } catch (e) {}
//        document.getElementById('playerholder').width = document.getElementById('videoarea').clientWidth - 30;
//        document.getElementById('playerholder').height = document.getElementById('playerholder').width * (9/16);
      },
      onPlayerReady: function(event) {
//        event.target.playVideo();
      },
      onPlayerStateChange: function(event) {
        if (event.data == YT.PlayerState.PLAYING && !this.done) {

        }

        if (event.data == YT.PlayerState.PAUSED) {
          this.show_overlay = true;
        }
        if (event.data == YT.PlayerState.PLAYING) {
          this.show_overlay = false;
        }
      },
      stopVideo: function() {
        this.player.stopVideo();
      },
      loadVideo: function() {
        var startTime = 0;
        if (typeof this.$route.query.t !== 'undefined') {
          // todo - change to support float seconds using seekTo
          startTime = parseInt(this.$route.query.t);
        }

        this.player = new YT.Player('player', {
//          height: '100%', //window.innerWidth / 4 * 2,
//          width: '100%',
          playerVars: {controls: 1, modestbranding: 0, autoplay: 1, start: startTime},
          videoId: this.videoid,
          events: {
            'onReady': this.onPlayerReady,
            'onStateChange': this.onPlayerStateChange
          }
        });

      },

      playVideo: function(playback_rate_index) {
        this.current_playback_rate_index = playback_rate_index;
        this.player.setPlaybackRate(this.playback_rates[this.current_playback_rate_index]);
        this.player.playVideo();
      }

    },
    mounted: function() {
      // todo - make it load without this hack
      // this is needed because YT player API is declared/loaded globally and don't know how to notify vue component when ready
      var cmp = this;
      var ii = setInterval(function() {
        if (window.youtubeAPIReady) {
          cmp.loadVideo();
          clearInterval(ii);
          cmp.resizeVideo(); // todo - check this always fires
          window.addEventListener('resize', cmp.resizeVideo);
        }}, 10);

      // add basic keyboard shortcuts
      var cmp = this;
      window.video_key_listener = function(event) {
        if (event.keyCode == 32) { // spacebar play/pause
          if (cmp.player.getPlayerState() == 1) {
            event.preventDefault();
            cmp.player.pauseVideo();
          } else if (cmp.player.getPlayerState() == 2) {
            event.preventDefault();
            cmp.player.playVideo();
          }
        }
        if (event.keyCode == 190  && event.shiftKey) { // shift + > to increase playback rate
          if (cmp.current_playback_rate_index < cmp.playback_rates.length - 1) {
            cmp.current_playback_rate_index++;
            cmp.player.setPlaybackRate(cmp.playback_rates[cmp.current_playback_rate_index]);
          }
        }
        if (event.keyCode == 188  && event.shiftKey) { // shift + < to decrease playback rate
          if (cmp.current_playback_rate_index > 0) {
            cmp.current_playback_rate_index--;
            cmp.player.setPlaybackRate(cmp.playback_rates[cmp.current_playback_rate_index]);
          }
        }
      }
      window.addEventListener('keydown', window.video_key_listener);

    },
    beforeDestroy: function() {
      this.player.destroy();
      window.removeEventListener('keydown', window.video_key_listener);
    }
  }
</script>