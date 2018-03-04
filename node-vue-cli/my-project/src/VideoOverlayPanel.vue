<template>
  <div @click="overlayClick">

<!--    <b-card v-if="show_options" no-body class="w-75 h-75 mx-auto centeredpanel"> //-->
    <b-card v-if="show_options" no-body class="mx-auto centeredpanel" style="width:300px;height:130px">
      <b-tabs pills card>
        <b-tab title="Playback" active>

          <b-form-radio-group id="btnradios2"
                          buttons
                          button-variant="outline-primary"
                          size="md"
                          v-model="playback_rate_index"
                          :options="playback_rate_options"
                          name="radioBtnOutline" />

        </b-tab>

        <b-tab title="Share">
          <b-button size="sm" @click="copyShareLink1ToClipboard" v-text="copy_button_1_text"></b-button>
          <b-button size="sm" @click="copyShareLink2ToClipboard" v-text="copy_button_2_text"></b-button>
        </b-tab>

      </b-tabs>
    </b-card>

    <icon v-if="!show_options" class="m-3" :color="'yellow'" name="pause" scale="2"></icon>

  </div>
</template>

<script>
  import { bus } from './main.js'
  export default {
    name: 'videooverlaypanel',
    props: ['initialPlaybackRateIndex'],
    mounted: function() {
    },
    methods: {      
      // todo move to globals
      getBasePath: function() {
        if (window.location.hostname == 'localhost') {
            return window.location.protocol + '//' + window.location.hostname + ':' + window.location.port;
        } else {
            return window.location.protocol + '//' + window.location.hostname;
        }
      },

      copyTextToClipboard: function(text) {
          function handler (event){
              event.clipboardData.setData('text/plain', text);
              event.preventDefault();
              document.removeEventListener('copy', handler, true);
          }
          document.addEventListener('copy', handler, true);
          document.execCommand('copy');
      },
      copyShareLink1ToClipboard: function(event) {
          this.copyTextToClipboard(this.getBasePath() + this.$route.path);
          this.copy_button_1_text = 'Copied to Clipboard!';
          event.preventDefault();
          event.stopPropagation();
      },
      copyShareLink2ToClipboard: function(event) {
          this.copyTextToClipboard(this.getBasePath() + this.$route.path + '?t=' + this.$parent.getCurrentTime());
          this.copy_button_2_text = 'Copied to Clipboard!';
          event.preventDefault();
          event.stopPropagation();
      },

      overlayClick: function() {
        if (this.show_options) {
          this.show_options=false;
          this.$emit('restartPlayback', this.playback_rate_index);
        } else {
          this.show_options=true;
        }
      },

      // sharing function for Android
      launchNativeShare: function() {
        if (navigator.share) {
          navigator.share({
              title: this.$parent.$parent.info.title,
              text: 'View on multi.tube',
              url: this.getBasePath() + this.$route.path + '?t=' + this.$parent.getCurrentTime()
          })
            .then(() => console.log('Successful share'))
            .catch((error) => console.log('Error sharing', error));
        }
      }

    },
    watch: {
      playback_rate_index: function(val) {
        this.$emit('restartPlayback', val);
      }
    },
    data () {
      return {
        show_options: false,
        playback_rate_index: this.initialPlaybackRateIndex,
        playback_rate_options: [{text: '1X', value: 2}, {text: '1.25X', value: 3}, {text: '1.5X', value: 4}, {text: '2X', value: 5}],
        copy_button_1_text: 'Copy Link',
        copy_button_2_text: 'Copy Link with Position'
    }
  }
}

</script>

<style scoped>
  .videooverlaypanel {
    padding: 0em;
    border: none;
  }

  .centeredpanel {
    position: relative;
    top: 50%;
    transform: translateY(-50%);    
  }

</style>

<style>
  .card-header {
    padding: 0px!important;
  }
</style>