<template>
  <div>
    <div style="position:relative" id="playerholder">
      <div id="player"></div>
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
    name: 'player-youtube',
    props: ['videoid'],
    data() {
      return { 
        player: null,
        done: false,
        overlay: false
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
        if (event.data == YT.PlayerState.PLAYING && !this.done) {

        }        
      },
      stopVideo: function() {
        this.player.stopVideo();
      },
      loadVideo: function() {
        this.player = new YT.Player('player', {
//          height: '100%', //window.innerWidth / 4 * 2,
//          width: '100%',
          playerVars: {controls: 1, modestbranding: 0, autoplay: 1},
          videoId: this.videoid,
          events: {
            'onReady': this.onPlayerReady,
            'onStateChange': this.onPlayerStateChange
          }
        });

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
    },
    beforeDestroy: function() {
      this.player.destroy();
    }
  }
</script>