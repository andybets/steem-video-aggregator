<template>
  <div class='playpage'>
    <b-container fluid class="overallpanel">
      <b-row no-gutters>
        <b-col cols="12" xl="10">
          <b-container class="leftpanel">
            <b-row>
              <b-col>
                <b-container fluid class="videopanel">
                  <b-row >
                    <b-col id="videoarea">
                      <player-youtube v-if="info.video_type=='youtube'" :videoid="info.video_id"></player-youtube>
                      <player-dtube v-if="info.video_type=='dtube'" :videoid="info.video_id"></player-dtube>
                      <player-dlive v-if="info.video_type=='dlive'" :videoid="info.video_id"></player-dlive>
                    </b-col>
                  </b-row>
                </b-container>    
              </b-col>
            </b-row>
            <b-row>
              <b-col>
                <b-container fluid class="titlepanel">
                  <b-row>
                    <b-col>
                      <h4 v-text="info.title"></h4>
                    </b-col>
                  </b-row>
                  <b-row>
                    <b-col cols="auto">
                      <b-img :src="'https://img.busy.org/@' + info.author + '?width=40&height=40'" rounded="circle" blank-color="#777"/>
                    </b-col>                    
                    <b-col>
                      <span v-for="tag in info.tags"><b-badge v-text="tag" variant="secondary"></b-badge>&nbsp;</span><br>
                      <a :href="'https://steemit.com/@' + info.author"><b v-text="info.author"></b></a> - {{ info.age_string }}
                       on 
                      <a v-if="info.video_type=='dtube'" :href="'https://d.tube/#!/v/' + info.author + '/' + info.permlink" target="_blank">
                        <b-img src='/dist/images/dtube-icon.png'/>
                      </a>
                      <a v-if="info.video_type=='dlive'" :href="'https://www.dlive.io/#/video/' + info.author + '/' + info.permlink" target="_blank">
                        <b-img src='/dist/images/dlive-icon.png'/>
                      </a>
                      <a v-if="info.video_type=='youtube'" :href="'https://www.youtube.com/watch?v=' + info.video_id" target="_blank">
                        <b-img src='/dist/images/youtube-icon.png'/>
                      </a>
                    </b-col >
                    <b-col cols="auto">
                      <div v-text="info.payout_string" class="float-right" style="font-size:1.1em;font-weight:800;"></div>
                    </b-col>
                  </b-row>
                </b-container>
              </b-col>
            </b-row>
            <b-row>
              <b-col>

                <b-container fluid class="bodypanel">
                  <b-row>
                    <b-col>
                        <div v-html="info.description"></div>
                    </b-col>
                  </b-row>
                </b-container>    
              </b-col>
            </b-row>
            <b-row>
              <b-col>

                <b-container fluid class="commentspanel">
                  <b-row>
                    <b-col>
                      <h5>Comments</h5>
                    </b-col>
                  </b-row>

                  <b-row v-for="comment in info.comments" :key="comment.permlink">
                    <b-col>
                      <b-container class="py-2">
                        <b-row no-gutters>
                          <b-col cols="auto">
                            <b-img :src="'https://img.busy.org/@' + comment.author + '?width=40&height=40'" rounded="circle" blank-color="#777"/>
                          </b-col>
                          <b-col>
                            <b-container fluid>
                              <b-row>
                                <b-col>
                                  <a :href="'https://steemit.com/@' + comment.author"><b v-text="comment.author"></b></a> - {{ comment.age_string }} - {{ comment.payout_string }}
                                </b-col>
                              </b-row>
                              <b-row>
                                <b-col>
                                  <div v-html="comment.body"></div>
                                </b-col>
                              </b-row>
                              <b-row>
                                <b-col>
                                  <div v-if="comment.reply_count == 1"><b>Show reply</b></div>
                                  <div v-else-if="comment.reply_count > 1"><b>Show {{ comment.reply_count }} replies</b></div>
                                </b-col>
                              </b-row>

                            </b-container>

                          </b-col>
                        </b-row>
                      </b-container>

                    </b-col>
                  </b-row>
                </b-container>    
              </b-col>
            </b-row>
          </b-container>    
        </b-col>
        <b-col>
          <b-container class="rightpanel">
            <b-row>
              <b-col>
                <b-container class="videolistpanel">
                  <b-row>
                    <b-col>
                      Related Videos
                    </b-col>
                  </b-row>
                </b-container>    
              </b-col>
            </b-row>
          </b-container>    
        </b-col>
      </b-row>
    </b-container>    
  </div>
</template>

<script>
  import bus from './main.js'
  export default {
    name: 'playpage',
    data () {
      return {
        info: {},
        video_id: ''
      }
    },
    methods: {
      loadVideoInfo: function() {
        var author = this.$route.params.author;
        var permlink = this.$route.params.permlink;
        this.$http.get('/f/api/video/@' + author + '/' + permlink)
         .then(response => {
            this.info = response.data;
            this.video_id = this.info.video_id;
        });
      }
    },
    created: function() {
      this.loadVideoInfo();
      window.scrollTo(0, 0);
    }
  }
</script>

<style>

h1, h2 {
  font-weight: normal;
}

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

.overallpanel {
    max-width: none;
}

@media (max-width: 1200px) {
  .rightpanel {
    display:none;
  }
}

.rightpanel {
  padding: 0px;
  padding-right:15px;
}

.videolistpanel {
  border: 1px solid #EAEAEA;
  margin-left:10px;
  margin-right:10px;
  background-color: white;
  padding: 10px;
}

.leftpanel {
  padding:0px;
}
.videopanel {
  padding:0px;
}
.overallpanel {
 padding:0px; 
}

.titlepanel {
  border: 1px solid #EAEAEA;
  padding: 1em;
  margin-top:10px;
  background-color: white;
}

.bodypanel {
  border: 1px solid #EAEAEA;
  padding: 1em;
  margin-top:10px;
  background-color: white;
}

.commentspanel {
  border: 1px solid #EAEAEA;
  padding: 1em;
  margin-top:10px;
  background-color: white;
}
</style>
