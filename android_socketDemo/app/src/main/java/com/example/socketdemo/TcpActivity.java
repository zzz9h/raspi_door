package com.example.socketdemo;

import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ImageView;

import androidx.appcompat.app.AppCompatActivity;

import java.io.IOException;

public class TcpActivity extends AppCompatActivity {
    private Button sendBtn;
    private Button openbtn;
    private Button closebtn;
    private EditText editText;
    private TextView contentTv;
    private TcpClientBiz clientBiz;
    private EditText edIp;
    private EditText edPort;
    private Button connection;
    private TextView title;
    private ImageView img;
    int f=1;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        initView();
        title = findViewById(R.id.id_title);
        title.setText("智慧门锁");
    }

    private void initView() {
        sendBtn = findViewById(R.id.send_btn);
        openbtn = findViewById(R.id.open_btn);
        closebtn = findViewById(R.id.close_btn);
        editText = findViewById(R.id.ed_msg);
        contentTv = findViewById(R.id.text_content);
        edIp = findViewById(R.id.ed_ip);
        edPort = findViewById(R.id.ed_port);
        connection = findViewById(R.id.connection_btn);

        connection.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                String ip = edIp.getText().toString();
                String port = edPort.getText().toString();
                if (!TextUtils.isEmpty(ip) && !TextUtils.isEmpty(port)) {
                    Integer dk = Integer.valueOf(port);
                    try {
                        clientBiz  = new TcpClientBiz(ip,dk);
                        if (clientBiz != null) {
                            Log.d("测试", "onCreate: listenner");
                            clientBiz.setOnMsgReturnedListenner(new TcpClientBiz.OnMsgReturnedListenner() {
                                @Override
                                public void OnMsgReturned(String msg) {
                                    Log.d("测试", "onCreate:msg");
                                    appendMsgToContent(msg + "");
                                }

                                @Override
                                public void OnFailure(Exception e) {
                                    e.printStackTrace();
                                }
                            });
                        }
                    } catch (Exception e) {
                        appendMsgToContent("Error:"+e);
                    }
                } else {
                    Toast.makeText(TcpActivity.this,"IP和端口不能为空",Toast.LENGTH_SHORT).show();
                }
            }
        });

        sendBtn.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        final String str = editText.getText().toString();
                        editText.setText("");
                        if (TextUtils.isEmpty(str)){
                            return;
                        }
                        if (clientBiz != null) {
                            clientBiz.SendMsg(str);
                        }else {
                            clientBiz.SendMsg(str);
                        }
            }
        });
        openbtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (clientBiz != null) {
                    clientBiz.SendMsg("开门");
                }else {
                    clientBiz.SendMsg("开门");
                }
            }
        });
        closebtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (clientBiz != null) {
                    clientBiz.SendMsg("关门");
                }else {
                    clientBiz.SendMsg("关门");
                }
            }
        });
    }

    public void appendMsgToContent(String msg){

        if (f==2)
        {
            contentTv.append(msg+"\n");
            f=0;
        }
        if (f==1) {
            contentTv.append(msg);
        }
        f++;
    }

    @Override
    protected void onDestroy() {
        if (clientBiz != null) {
            try {
                clientBiz.onTcpDestroy();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        super.onDestroy();
    }
}
