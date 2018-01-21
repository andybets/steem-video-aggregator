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
    },
    beforeDestroy: function() {
//      this.player.destroy();
    }
  }
</script>

