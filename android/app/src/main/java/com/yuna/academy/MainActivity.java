package com.yuna.academy;

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.net.Uri;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.ProgressBar;
import android.graphics.Color;
import android.webkit.DownloadListener;

public class MainActivity extends Activity {
  private WebView web;
  private ProgressBar progress;
  private static final String HOME = "https://yuna-academy.vercel.app/";
  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    getWindow().setStatusBarColor(Color.rgb(250,247,241));
    getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
    FrameLayout layout = new FrameLayout(this);
    web = new WebView(this);
    progress = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
    progress.setMax(100);
    FrameLayout.LayoutParams bar = new FrameLayout.LayoutParams(-1, 6);
    bar.gravity = android.view.Gravity.TOP;
    layout.addView(web);
    layout.addView(progress, bar);
    setContentView(layout);
    WebSettings settings = web.getSettings();
    settings.setJavaScriptEnabled(true);
    settings.setDomStorageEnabled(true);
    settings.setMediaPlaybackRequiresUserGesture(true);
    settings.setAllowFileAccess(false);
    settings.setAllowContentAccess(false);
    settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
    web.setWebChromeClient(new WebChromeClient(){
      @Override public void onProgressChanged(WebView view,int value){
        progress.setProgress(value);
        progress.setVisibility(value>=100?View.GONE:View.VISIBLE);
      }
    });
    web.setWebViewClient(new WebViewClient(){
      @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){
        Uri uri=request.getUrl();
        if("https".equals(uri.getScheme()) && "yuna-academy.vercel.app".equals(uri.getHost())) return false;
        if(!request.isForMainFrame())return false;
        try { startActivity(new Intent(Intent.ACTION_VIEW,uri)); } catch(Exception ignored){}
        return true;
      }
    });
    web.setDownloadListener((url,ua,disposition,mime,length)->{
      try { startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(url))); }catch(Exception ignored){}
    });
    if(state==null)web.loadUrl(HOME);else web.restoreState(state);
  }
  @Override protected void onSaveInstanceState(Bundle state){super.onSaveInstanceState(state);web.saveState(state);}
  @Override public void onBackPressed(){if(web.canGoBack())web.goBack();else super.onBackPressed();}
  @Override protected void onDestroy(){web.destroy();super.onDestroy();}
}
