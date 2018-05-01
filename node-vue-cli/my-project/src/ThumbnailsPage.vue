<template>
  <div class='thumbnailspage'>

    <b-container class="video-horizontal-panel">
      <h4 v-if="videos.length>0" style="padding-left:10px">{{ page_title }}<span style="color:red;font-size: 0.7em;" v-if="$globals.filter_not_default"> (filtered)</span></h4>
      <b-row>

        <b-col class="px-0" sm="6" md="4" lg="3" xl="2" v-for="v in videos" :key="v.author + v.permlink">
            <div style="padding-bottom:15px">
                <div style="position:relative;padding:5px">
                    <span class="duration-label">&nbsp;{{ v.duration_string }}&nbsp;</span>
                    <div style="cursor:pointer;z-index:998;background-color:rgb(0,0,0);">
                        <b-img-lazy offset="1000" @contextmenu.native.prevent="playVideo(v.author, v.permlink, v.video_type, v.video_id, true)" v-on:click.native="playVideo(v.author, v.permlink, v.video_type, v.video_id, false)" center fluid :src="v.video_thumbnail_image_url" class="thumbnail-image"/> 
                    </div>
                </div>
                <div class="video-info-panel">
                  <div class="video-title" v-on:click="playVideo(v.author, v.permlink, v.video_type, v.video_id)" v-text="v.title_truncated"></div>
                  <div class="video-author-age">
                  <span class="author-link" @click="authorLinkClicked(v.author)">{{ v.author }}</span> - 
                    <span v-if="v.video_post_delay_days==0"><font color="#66BB66">{{ v.age_string }}</font></span>
                    <span v-else-if="v.video_post_delay_days<=7">{{ v.age_string }}</span>
                    <span v-else=""><font color="#BB6666">{{ v.age_string }}</font></span> 
                    on 
                    <a v-if="v.video_type=='dtube'" :href="'https://d.tube/#!/v/' + v.author + '/' + v.permlink" target="_blank">
                      <b-img src='/dist/images/dtube-icon.png'/>
                    </a>
                    <a v-if="v.video_type=='dlive'" :href="'https://www.dlive.io/#/video/' + v.author + '/' + v.permlink" target="_blank">
                      <b-img src='/dist/images/dlive-icon.png'/>
                    </a>
                    <a v-if="v.video_type=='youtube'" :href="'https://www.youtube.com/watch?v=' + v.video_id" target="_blank">
                      <b-img src='/dist/images/youtube-icon.png'/>
                    </a>
                  </div>
                  <div style="text-align:center">
                    <span class="video-payout-string">{{ v.payout_string }}</span>
                    <trend v-if="v.votes_sparkline_data" 
                      :width="30"
                      :height="12"
                      :data="JSON.parse(v.votes_sparkline_data)"
                      :gradient="['#333', '#333', '#333']"
                      :stroke-width="1"
                      :padding="1" 
                      >
                    </trend>
                  </div>
                </div>
            </div>
        </b-col>

        <infinite-loading ref="infiniteLoading" @infinite="infiniteHandler">
          <span slot="no-results"></span>
        </infinite-loading>

      </b-row>
    </b-container>

  </div>
</template>

<script>
  import { bus } from './main.js'
  export default {
    name: 'thumbnailspage',
    props: ['page_title', 'video_list_url'],
    watch: {
      '$route': 'fetchData'
    },
    methods: {
      authorLinkClicked: function(author) {
        bus.$emit('authorLinkClicked', author)
      },
      playVideo: function(author, permlink, video_type, video_id, new_tab) {
        // temporarily used on right-click to open new tab
        // todo - replace with context menu
        if (new_tab) {
          event.preventDefault();
          if (video_type=='dlive' && video_id == 'live') {
            var url = 'https://www.dlive.io/#/video/' + author + '/' + permlink;
          } else {
            var url = '/@' + author + '/' + permlink
          }
          setTimeout(function() {
            window.open(url, '_blank')
          }, 100);
          return;
        }


        if (video_type=='dlive' && video_id == 'live') {
          window.location.href = 'https://www.dlive.io/#/video/' + author + '/' + permlink;
        }
        this.$router.push('/@' + author + '/' + permlink);
      },
      fetchData: function() {
        console.log(this.video_list_url);
        this.thumbnail_target = 50;
        this.$refs.infiniteLoading.stateChanger.reset();
        var filter_data = {
              filter_age_selection: this.$globals.filter_age_selection,
              filter_included_types: this.$globals.filter_included_types,
              filter_duration_selection: this.$globals.filter_duration_selection,
              filter_sort_selection: this.$globals.filter_sort_selection,            
              filter_exclude_old_video: this.$globals.filter_exclude_old_video,
              filter_exclude_nsfw: this.$globals.filter_exclude_nsfw,
              filter_excluded_voters: this.$globals.filter_excluded_voters,
              filter_included_voters: this.$globals.filter_included_voters,
              filter_excluded_authors: this.$globals.filter_excluded_authors,
              filter_included_authors: this.$globals.filter_included_authors,
              filter_excluded_tags: this.$globals.filter_excluded_tags,
              filter_included_tags: this.$globals.filter_included_tags,
              filter_reputation_active: this.$globals.filter_reputation_active,
              filter_quick_play_enabled: this.$globals.filter_quick_play_enabled
            }
        var rr = this;
        setTimeout(function() {
          var rrr = rr;

          var query_string = '';
          if (rr.video_list_url == '/f/api/account-videos') {
            query_string = '/' + rr.$route.params.author;
          }

          rr.$http.post(rr.video_list_url + query_string + '/' + rr.thumbnail_target, filter_data)
           .then(response => {
            rrr.videos = response.data.filter(function(result) {
              return true;
            });
            rrr.loadNewlyDisplayedImages();
          });
        }, 100);

      },

      infiniteHandler($state) {
        this.thumbnail_target += 50;
        var filter_data = {
              filter_age_selection: this.$globals.filter_age_selection,
              filter_included_types: this.$globals.filter_included_types,
              filter_duration_selection: this.$globals.filter_duration_selection,
              filter_sort_selection: this.$globals.filter_sort_selection,            
              filter_exclude_old_video: this.$globals.filter_exclude_old_video,
              filter_exclude_nsfw: this.$globals.filter_exclude_nsfw,
              filter_excluded_voters: this.$globals.filter_excluded_voters,
              filter_included_voters: this.$globals.filter_included_voters,
              filter_excluded_authors: this.$globals.filter_excluded_authors,
              filter_included_authors: this.$globals.filter_included_authors,
              filter_excluded_tags: this.$globals.filter_excluded_tags,
              filter_included_tags: this.$globals.filter_included_tags,
              filter_reputation_active: this.$globals.filter_reputation_active,
              filter_quick_play_enabled: this.$globals.filter_quick_play_enabled
            }
        // gets whole new results set rather than extending, as new entries could make using offsets difficult
        var query_string = '';
        if (this.video_list_url == '/f/api/account-videos') {
          query_string = '/' + this.$route.params.author;
        }

//        this.$http.post(this.video_list_url + '/' + this.thumbnail_target, filter_data)
        this.$http.post(this.video_list_url + query_string + '/' + this.thumbnail_target, filter_data)
         .then(response => {
            console.log(response.body.length);
            this.videos = response.data.filter(function(result) {
              return true;
            });
            this.loadNewlyDisplayedImages();
            // if server didn't send requested number of videos, prevent further load attempts
            if (this.videos.length < this.thumbnail_target) {
              $state.complete();
            } else {
              $state.loaded();
            }
          })
       },

      // todo - remove this hack for loading lazy images
      loadNewlyDisplayedImages: function() {
        for (var i=0; i<4; i++) {
          window.setTimeout(function() {window.dispatchEvent(new Event('resize'))}, 200);
          window.setTimeout(function() {window.scroll(window.scrollX, window.scrollY+1)}, 200*i);
          window.setTimeout(function() {window.scroll(window.scrollX, window.scrollY-1)}, 200*i);
        }
      }

    },
    data () {
      return {
        videos: [],
        thumbnail_target: 50
    }
  },
  activated: function() {
    this.fetchData();

    var cmp = this;
    setTimeout(function() {
      bus.$on('filtersChanged', cmp.fetchData);
      console.log('Added filtersChanged event handler in thumbnails.');
    }, 500)    
  },
  deactivated: function() {
    bus.$off('filtersChanged');
    console.log('Removed filtersChanged event handler in thumbnails.');
  },

}

</script>

<style scoped>

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}

.video-info-panel {
  padding-left:7px;
  padding-right:5px;
  line-height: 1.1em;
  text-align: center;
}

.video-title {
  font-family: 'Roboto', 'Helvetica Neue', Arial, Helvetica, sans-serif;
  font-weight: 800;
  font-size: 0.8rem; 
  cursor: pointer;
}

.video-author-age {
  padding-top: 5px;
  font-family: 'Roboto', 'Helvetica Neue', Arial, Helvetica, sans-serif;
  color: grey;
  font-size: 0.8rem; 
}

.video-payout-string {
  font-family: 'Roboto', 'Helvetica Neue', Arial, Helvetica, sans-serif;
  font-size: 0.85rem; 
}

.video-age-string {
  font-family: 'Roboto', 'Helvetica Neue', Arial, Helvetica, sans-serif;
  color: grey;
  font-size: 0.8rem; 
}


.duration-label {
  font-size:0.8em;
  position:absolute;
  bottom:10px;
  right:10px;
  background-color:rgb(0,0,0);
  color:white;
}

.navbar-braond {
  margin-right: 0px;
}

/* prevent carousel pagination showing - shouldn't be needed */
.VueCarousel-pagination {
  display:none;
}

.VueCarousel-navigation--disabled{
  opacity: 0.1!important;
}

.video-horizontal-panel {
    max-width: none;
}

.video-horizontal-panel {
  padding-left:0px;
  padding-right:0px;
}

.infinite-status-prompt {
  display:none;
}


.video-horizontal-panel {
  padding-left:25px;
  padding-right:25px;
}
@media (min-width: 768px) {
  .video-horizontal-panel {
    padding-left:55px;
    padding-right:55px;
  }
}

/* enlarge thumbnail height for phones */
@media (max-width: 767px) {
  .thumbnail-image {
    height: 25vh;
  }
}
@media (min-width: 768px) {
  .thumbnail-image {
    height: 17vh;
  }
}



</style>

