<template>
  <div class='playpage'>
    <b-container class="overallpanel px-xl-5">
      <b-row no-gutters>
        <b-col cols="12" xl="9" >

          <b-container fluid class="leftpanel px-lg-2 pl-xl-5">
            <b-row>
              <b-col>
                <b-container fluid class="videopanel px-lg-5 px-xl-0">
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
                      <b-img :src="'https://steemitimages.com/u/' + info.author + '/avatar/small'" rounded="circle" blank-color="#777" style="width:40px;height:40px"/>
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

                      <div id="popoverPayout-sync" v-text="info.payout_string" class="float-right" style="cursor:pointer;font-size:1.2em;font-weight:800;"></div>
                      <b-popover :show.sync="show_vote_contributions" target="popoverPayout-sync" title="Vote Contributions">
                        <div style="width:200px;height:1px"></div> 
                        <b-container v-if="show_vote_contributions" class="px-0 mx-0" v-click-outside="closeVoteContributions">
                          <b-row no-gutters>
                            <b-col cols="12" >
                              <b-container style="border-bottom:1px solid #EEEEEE;" class="px-0 mx-0" v-for="c in info.vote_contributions" :key="c.voter">
                                <b-row no-gutters>
                                  <b-col cols="7">
                                    <a style="font-weight:800" v-if="c.voter==$globals.username" v-text="c.voter" :href="'https://steemit.com/@' + c.voter" target="_blank"></a>
                                    <a v-else v-text="c.voter" :href="'https://steemit.com/@' + c.voter" target="_blank"></a>
                                  </b-col>
                                  <b-col cols="5" style="text-align:right">
                                    <span v-html="c.contribution"></span>
                                  </b-col>
                                </b-row>
                              </b-container>
                            </b-col>
                          </b-row>
                        </b-container>
                      </b-popover>


                      <div style="text-align:center">
                        <icon v-if="up_voting" :color="'green'" name="spinner" scale="1.5" spin></icon>
                        <icon id="popoverUpVote-sync" v-else :color="up_vote_hover||up_voted ? 'green' : 'grey'" name="arrow-circle-up" scale="1.75" @mouseover.native="up_vote_hover=true"  @mouseleave.native="up_vote_hover=false" @click.native="checkUpVote"></icon>
                        <b-popover :show.sync="show_up_vote_slider" target="popoverUpVote-sync">
                          <div style="width:300px;height:1px"></div>
                          <b-container v-if="show_up_vote_slider" v-click-outside="closeVoteSliders">
                            <b-row no-gutters>
                              <b-col cols="12">
                                <vue-slider ref="up_vote_slider" v-model="vote_percent"></vue-slider>
                              </b-col>
                            </b-row>
                          </b-container>
                        </b-popover>

                        <icon v-if="down_voting" :color="'red'" name="spinner" scale="1.5" spin></icon>
                        <icon id="popoverDownVote-sync" v-else :color="down_vote_hover||down_voted ? 'red' : 'grey'" name="arrow-circle-down" scale="1.75" @mouseover.native="down_vote_hover=true"  @mouseleave.native="down_vote_hover=false"  @click.native="checkDownVote"></icon>
                        <b-popover :show.sync="show_down_vote_slider" target="popoverDownVote-sync">
                          <div style="width:300px;height:1px"></div> 
                          <b-container v-if="show_down_vote_slider" v-click-outside="closeVoteSliders">
                            <b-row no-gutters>
                              <b-col cols="12">
                                <vue-slider ref="down_vote_slider" v-model="vote_percent"></vue-slider>
                              </b-col>
                            </b-row>
                          </b-container>
                        </b-popover>

                      </div>

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
                      <b-container class="pt-2 mx-0">
                        <b-row no-gutters>
                          <b-col cols="auto">
                            <h5>Comments</h5>
                          </b-col>
                        </b-row>
                      </b-container>
                    </b-col>
                  </b-row>

                  <!-- load 1st level comments with main content, but other levels as requested //-->
                  <b-row v-for="comment in info.comments" :key="comment.permlink">
                    <b-col>
                      <b-container class="pt-3 pb-2 mx-0">
                        <b-row no-gutters>
                          <b-col cols="auto">
                            <b-img :src="'https://steemitimages.com/u/' + comment.author + '/avatar/small'" rounded="circle" blank-color="#777" style="width:40px;height:40px"/>
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
                                  <replies-panel v-if="comment.reply_count>0" :author="comment.author" :permlink="comment.permlink" :reply_count="comment.reply_count"></replies-panel>
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

          <b-container class="rightpanel pr-lg-2 pr-xl-5">
            <b-row>
              <b-col>
                <b-container class="rightpanel-placeholder">
                  <b-row>
                    <b-col>
                      Right Panel Placeholder
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
    props: ['author', 'permlink'],
    data () {
      return {
        info: {},
        video_id: '',
        vote_percent: this.$globals.default_vote_percent,
        up_vote_hover: false,
        down_vote_hover: false,
        show_up_vote_slider: false,
        show_down_vote_slider: false,
        up_voting: false,
        down_voting: false,
        up_voted: false,
        down_voted: false,

        show_vote_contributions: false
      }
    },
    methods: {
      loadVideoInfo: function() {
        this.$http.get('/f/api/video/@' + this.author + '/' + this.permlink)
         .then(response => {
            this.info = response.data;
            this.video_id = this.info.video_id;
            this.$globals.getVotesInfo(this.info.author, this.info.permlink, this.displayVoteInfo, null);
        });
      },

      checkUpVote: function() {
        if (this.show_up_vote_slider) {
          var cmp = this
          if (this.vote_percent > 0) { this.up_voting = true; }
          this.$globals.vote(this.info.author, this.info.permlink, parseInt(this.vote_percent*100), function() {
              cmp.$globals.getVotesInfo(cmp.info.author, cmp.info.permlink, cmp.displayVoteInfo, null);
          }, function() {
              cmp.$globals.getVotesInfo(cmp.info.author, cmp.info.permlink, cmp.displayVoteInfo, null);
          });
        }
      },
      checkDownVote: function() {
        if (this.show_down_vote_slider) {
          var cmp = this
          if (this.vote_percent > 0) { this.down_voting = true; }
          this.$globals.vote(this.info.author, this.info.permlink, -parseInt(this.vote_percent*100), function() {
              cmp.$globals.getVotesInfo(cmp.info.author, cmp.info.permlink, cmp.displayVoteInfo, null);
          }, function() {
              cmp.$globals.getVotesInfo(cmp.info.author, cmp.info.permlink, cmp.displayVoteInfo, null);
          });
        }
      },

      displayVoteInfo: function(total_payout, up_voted, down_voted, vote_contributions) {
        this.up_voting = false;
        this.down_voting = false;
        this.up_voted = up_voted;
        this.down_voted = down_voted;
        this.info.payout_string = '$' + total_payout.toFixed(3);
        this.info.vote_contributions = vote_contributions;
        this.$globals.default_vote_percent = this.vote_percent;
      },

      closeVoteSliders: function() {
        this.show_up_vote_slider = false;
        this.show_down_vote_slider = false;
      },
      closeVoteContributions: function() {
        this.show_vote_contributions = false;
      }

    },
    created: function() {
      this.loadVideoInfo();
      window.scrollTo(0, 0);
    }
  }
</script>

<style scoped>

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

.rightpanel-placeholder {
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
  padding: 0px;
  padding-top: 0.5em;
  padding-bottom: 2em;
  margin-top:1em;
  background-color: white;
}

</style>

<style>
  .action-link {
    color: #000066;
    cursor: pointer;
    font-weight: 800;
  }
</style>