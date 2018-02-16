<template>
  <div class='homepage'>

    <b-container class="video-horizontal-panel">
      <h4 style="padding-left:10px"><router-link :to="{ path: '/hot' }">Hot Videos</router-link> <span style="color:red;font-size: 0.7em;" v-if="$globals.filter_not_default"> (filtered)</span> </h4>
      <carousel :minSwipeDistance="100" :perPage="1" :perPageCustom="[[601, 2], [801, 3], [1101, 4], [1351, 5], [1600, 6]]" navigationEnabled 
        navigationNextLabel="<img src='/dist/images/right-arrow.png'/>"
        navigationPrevLabel="<img src='/dist/images/left-arrow.png'/>"
        scrollPerPage @touchend.native="loadNewlyDisplayedImages" @mouseup.native="loadNewlyDisplayedImages">

        <!-- todo - improve lazy loading, currently in slide //-->
        <slide v-for="v in hot_videos" :key="v.author + v.permlink">
            <div>
                <div style="position:relative;padding:5px;margin-right:0px">
                    <span class="duration-label">&nbsp;{{ v.duration_string }}&nbsp;</span>
                    <div style="cursor:pointer;z-index:998;background-color:rgb(0,0,0);">
                        <b-img-lazy offset="1000" class="thumbnail-image" @contextmenu.native.prevent="playVideo(v.author, v.permlink, v.video_type, v.video_id, true)" v-on:click.native="playVideo(v.author, v.permlink, v.video_type, v.video_id, false)" center fluid :src="v.video_thumbnail_image_url"/>
                    </div>
                </div>
                <div class="video-info-panel">
                  <div class="video-title" v-on:click="playVideo(v.author, v.permlink, v.video_type, v.video_id)">{{ v.title_truncated }}</div>
                  <div class="video-author-age"><a target="_blank" :href="'https://steemit.com/@' + v.author ">{{ v.author }}</a> - 
                    <span v-if="v.video_post_delay_days==0"><font color="#66BB66">{{ v.age_string }}</font></span>
                    <span v-else-if="v.video_post_delay_days<=7">{{ v.age_string }}</span>
                    <span v-else=""><font color="#BB6666">{{ v.age_string }}</font></span>
                   on 
                    <a v-if="v.video_type=='dtube'" :href="'https://d.tube/#!/v/' + v.author + '/' + v.permlink" target="_blank">
                      <b-img src='/dist/images/dtube-icon.png'/>
                    </a>
                    <span v-if="v.video_type=='dlive'">
                      <a v-if="v.video_id=='live'" :href="'https://www.dlive.io/#/livestream/' + v.author + '/' + v.permlink" target="_blank">
                        <b-img style="background:#AAFFAA" src='/dist/images/dlive-icon.png'/>
                      </a>
                      <a v-else :href="'https://www.dlive.io/#/video/' + v.author + '/' + v.permlink" target="_blank">
                        <b-img src='/dist/images/dlive-icon.png'/>
                      </a>                      
                    </span>
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
                      :gradient="['#000', '#000', '#000']"
                      :stroke-width="1"
                      :padding="1" 
                      >
                    </trend>
                  </div>
                </div>
            </div>
        </slide>
      </carousel>
    </b-container>

    <hr>

    <b-container class="video-horizontal-panel">
      <h4 style="padding-left:10px"><router-link :to="{ path: '/trending' }">Trending Videos</router-link><span style="color:red;font-size: 0.7em;" v-if="$globals.filter_not_default"> (filtered)</span></h4>
      <carousel :minSwipeDistance="100" :perPage="1" :perPageCustom="[[601, 2], [801, 3], [1101, 4], [1351, 5], [1600, 6]]" navigationEnabled 
        navigationNextLabel="<img src='/dist/images/right-arrow.png'/>"
        navigationPrevLabel="<img src='/dist/images/left-arrow.png'/>"
        scrollPerPage @touchend.native="loadNewlyDisplayedImages" @mouseup.native="loadNewlyDisplayedImages">

        <!-- todo - improve lazy loading, currently in slide //-->
        <slide v-for="v in trending_videos" :key="v.author + v.permlink">
            <div>
                <div style="position:relative;padding:5px;margin-right:0px">
                    <span class="duration-label">&nbsp;{{ v.duration_string }}&nbsp;</span>
                    <div style="cursor:pointer;z-index:998;background-color:rgb(0,0,0);">
                        <b-img-lazy offset="1000" class="thumbnail-image" @contextmenu.native.prevent="playVideo(v.author, v.permlink, v.video_type, v.video_id, true)" v-on:click.native="playVideo(v.author, v.permlink, v.video_type, v.video_id, false)" center fluid :src="v.video_thumbnail_image_url"/> 
                    </div>
                </div>
                <div class="video-info-panel">
                  <div class="video-title" v-on:click="playVideo(v.author, v.permlink, v.video_type, v.video_id)">{{ v.title_truncated }}</div>
                  <div class="video-author-age"><a target="_blank" :href="'https://steemit.com/@' + v.author ">{{ v.author }}</a> - 
                    <span v-if="v.video_post_delay_days==0"><font color="#66BB66">{{ v.age_string }}</font></span>
                    <span v-else-if="v.video_post_delay_days<=7">{{ v.age_string }}</span>
                    <span v-else=""><font color="#BB6666">{{ v.age_string }}</font></span>
                   on 
                    <a v-if="v.video_type=='dtube'" :href="'https://d.tube/#!/v/' + v.author + '/' + v.permlink" target="_blank">
                      <b-img src='/dist/images/dtube-icon.png'/>
                    </a>
                    <span v-if="v.video_type=='dlive'">
                      <a v-if="v.video_id=='live'" :href="'https://www.dlive.io/#/livestream/' + v.author + '/' + v.permlink" target="_blank">
                        <b-img style="background:#AAFFAA" src='/dist/images/dlive-icon.png'/>
                      </a>
                      <a v-else :href="'https://www.dlive.io/#/video/' + v.author + '/' + v.permlink" target="_blank">
                        <b-img src='/dist/images/dlive-icon.png'/>
                      </a>                      
                    </span>
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
                      :gradient="['#000', '#000', '#000']"
                      :stroke-width="1"
                      :padding="1" 
                      >
                    </trend>
                  </div>
                </div>
            </div>
        </slide>
      </carousel>
    </b-container>

    <hr>

    <b-container class="video-horizontal-panel">
      <h4 style="padding-left:10px"><router-link :to="{ path: '/new' }">New Videos</router-link><span style="color:red;font-size: 0.7em;" v-if="$globals.filter_not_default"> (filtered)</span></h4>
      <carousel :minSwipeDistance="100" :perPage="1" :perPageCustom="[[601, 2], [801, 3], [1101, 4], [1351, 5], [1600, 6]]" navigationEnabled 
        navigationNextLabel="<img src='/dist/images/right-arrow.png'/>"
        navigationPrevLabel="<img src='/dist/images/left-arrow.png'/>"
        scrollPerPage @touchend.native="loadNewlyDisplayedImages" @mouseup.native="loadNewlyDisplayedImages">

        <!-- todo - improve lazy loading, currently in slide //-->
        <slide v-for="v in new_videos" :key="v.author + v.permlink">
            <div>
                <div style="position:relative;padding:5px">
                    <span class="duration-label">&nbsp;{{ v.duration_string }}&nbsp;</span>
                    <div style="cursor:pointer;z-index:998;background-color:rgb(0,0,0);">
                        <b-img-lazy offset="1000" class="thumbnail-image" @contextmenu.native.prevent="playVideo(v.author, v.permlink, v.video_type, v.video_id, true)" v-on:click.native="playVideo(v.author, v.permlink, v.video_type, v.video_id, false)" center fluid :src="v.video_thumbnail_image_url"/>
                    </div>
                </div>
                <div class="video-info-panel">
                  <div class="video-title" v-on:click="playVideo(v.author, v.permlink, v.video_type, v.video_id)">{{ v.title_truncated }}</div>
                  <div class="video-author-age"><a target="_blank" :href="'https://steemit.com/@' + v.author ">{{ v.author }}</a> - 
                    <span v-if="v.video_post_delay_days==0"><font color="#66BB66">{{ v.age_string }}</font></span>
                    <span v-else-if="v.video_post_delay_days<=7">{{ v.age_string }}</span>
                    <span v-else=""><font color="#BB6666">{{ v.age_string }}</font></span> 
                    on 
                    <a v-if="v.video_type=='dtube'" :href="'https://d.tube/#!/v/' + v.author + '/' + v.permlink" target="_blank">
                      <b-img src='/dist/images/dtube-icon.png'/>
                    </a>
                    <span v-if="v.video_type=='dlive'">
                      <a v-if="v.video_id=='live'" :href="'https://www.dlive.io/#/livestream/' + v.author + '/' + v.permlink" target="_blank">
                        <b-img style="background:#AAFFAA" src='/dist/images/dlive-icon.png'/>
                      </a>
                      <a v-else :href="'https://www.dlive.io/#/video/' + v.author + '/' + v.permlink" target="_blank">
                        <b-img src='/dist/images/dlive-icon.png'/>
                      </a>                      
                    </span>
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
        </slide>
      </carousel>
    </b-container>

    <hr>

  </div>
</template>

<script>
  import { bus } from './main.js'
  export default {
    name: 'homepage',
    methods: {
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

        // if dlive video was live at last check, send to live stream on dlive
        if (video_type=='dlive' && video_id == 'live') {
          window.location.href = 'https://www.dlive.io/#/livestream/' + author + '/' + permlink;
        } else {
          this.$router.push('/@' + author + '/' + permlink);
        }
      },
      fetchData: function() {
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
              filter_reputation_active: this.$globals.filter_reputation_active,
              filter_quick_play_enabled: this.$globals.filter_quick_play_enabled
            }
        var rr = this;
        this.$http.post('/f/api/trending-videos', filter_data)
         .then(response => {
          rr.trending_videos = response.data.filter(function(result) {
            return true;
          });
        });
        setTimeout(function() {
          var rrr = rr;
          rr.$http.post('/f/api/hot-videos', filter_data)
           .then(response => {
            rrr.hot_videos = response.data.filter(function(result) {
              return true;
            });
          });
        }, 100);
        this.$http.post('/f/api/new-videos', filter_data)
         .then(response => {
          rr.new_videos = response.data.filter(function(result) {
            return true;
          });
        });
      },
      preventTouchmove: function(e) { // to prevent iOS page moving on carousel swipe todo - remove function when known not needed
        e.preventDefault();        
      },
      // this triggers image display check, which carousel component should ideally do
      // todo - improve the lazy loading approach and remove this hack
      loadNewlyDisplayedImages: function() {
        for (var i=0; i<4; i++) {
          window.setTimeout(function() {window.scroll(window.scrollX, window.scrollY+1)}, 200*i);
          window.setTimeout(function() {window.scroll(window.scrollX, window.scrollY-1)}, 200*i);
        }
      }
    },
    data () {
      return {
        trending_videos: [],
        hot_videos: [],
        new_videos: []
    }
  },
  activated: function() {
    // prevent repeated initial fetches
    var cmp = this;
    setTimeout(function() {
      bus.$on('filtersChanged', cmp.fetchData);
      console.log('Added filtersChanged event handler in homepage.');
    }, 500)

    this.fetchData();
  },
  deactivated: function() {
    bus.$off();
    console.log('Removed filtersChanged event handler in homepage.');
  }

}

</script>

<style>
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
</style>

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

.video-horizontal-panel {
    max-width: none;
}

.video-horizontal-panel {
  padding-left:0px;
  padding-right:0px;
}


/* make space for video arrows */
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

.action-link {
  color: #000066;
  cursor: pointer;
  font-weight: 800;
}
</style>

