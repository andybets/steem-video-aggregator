<template>
  <div>
    <div style="position:relative" id="playerholder">
        <video id="player" controls>
            Your browser does not support the video tag.
       </video>
<!--      <div id="player"></div> //-->
      <div v-if="overlay" id="playeroverlay" style="background: rgba(100,100,100, 0.5); position:absolute; top:0; left:0; width:100%;height:99%; z-index:16777271;"></div>
      <!--
      <button style="position:absolute; top:0; left:0; width:20;height:20;z-index:16777271;" @click="overlay=!overlay">C</button>
      //-->
    </div>
  </div>    
</template>
<script>
  import Vue from 'vue'

  export default {
    name: 'player-dtube',
    props: ['videoid'],
    data() {
      return { 
        player: null,
        done: false,
        overlay: false,
        playback_rates: [0.25, 0.5, 1, 1.5, 2],
        current_playback_rate_index: 2
      }
    },
    methods: {
      resizeVideo: function() {
        document.getElementById('player').width = document.getElementById('videoarea').clientWidth - 30;
        document.getElementById('player').height = document.getElementById('player').width * (9/16);
//        document.getElementById('playerholder').width = document.getElementById('videoarea').clientWidth - 30;
//        document.getElementById('playerholder').height = document.getElementById('playerholder').width * (9/16);
      },
      onPlayerReady: function(event) {
//        event.target.playVideo();
      },
      onPlayerStateChange: function(event) {
      },
      stopVideo: function() {
//        this.player.stopVideo();
      },
      loadVideo: function() {
        var video = document.getElementById('player');
        var source = document.createElement('source');
        source.setAttribute('src', 'https://ipfs.io/ipfs/' + this.videoid);
        video.appendChild(source);
        video.play();
      }

    },
    mounted: function() {
      // todo - make it load without this hack
      var cmp = this;
      var ii = setTimeout(function() {
        cmp.loadVideo();
        cmp.resizeVideo(); // todo - check this always fires
        window.addEventListener('resize', cmp.resizeVideo);
      }, 10);

      // add basic keyboard shortcuts
      var cmp = this;
      window.key_listener = function(event) {
        if (event.keyCode == 32) { // spacebar play/pause
          if (!cmp.player.paused) {
            event.preventDefault();
            cmp.player.pause();
          } else {
            event.preventDefault();
            cmp.player.play();
          }
        }
        if (event.keyCode == 190  && event.shiftKey) { // shift + > to increase playback rate
          if (cmp.current_playback_rate_index < cmp.playback_rates.length - 1) {
            cmp.current_playback_rate_index++;
            cmp.player.playbackRate = cmp.playback_rates[cmp.current_playback_rate_index];
          }
        }
        if (event.keyCode == 188  && event.shiftKey) { // shift + < to decrease playback rate
          if (cmp.current_playback_rate_index > 0) {
            cmp.current_playback_rate_index--;
            cmp.player.playbackRate = cmp.playback_rates[cmp.current_playback_rate_index];
          }
        }
      }
      window.addEventListener('keydown', window.key_listener);

    },
    beforeDestroy: function() {
      window.removeEventListener('keydown', window.key_listener);
//      this.player.destroy();
    }
  }
</script>

