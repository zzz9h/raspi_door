package com.example.socketdemo;

import android.os.Handler;
import android.os.Looper;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.Socket;
import java.net.SocketException;
import java.net.UnknownHostException;


public class TcpClientBiz {
    private String serverIp;
    private int serverPort;
    private Socket mSocket;
    private OutputStream os = null;
    private InputStream is = null;
    private OnMsgReturnedListenner mListenner;

    private Handler handler = new Handler(Looper.getMainLooper());

    public TcpClientBiz(final String serverIp, final int serverPort) throws IOException {
        this.serverIp = serverIp;
        this.serverPort = serverPort;

        new Thread() {
            @Override
            public void run() {
                try {
                    mSocket = new Socket(serverIp, serverPort);
                    is = mSocket.getInputStream();
                    os = mSocket.getOutputStream();
                    readServerMsg();
                } catch (final Exception e) {
                    handler.post(new Runnable() {
                        @Override
                        public void run() {
                            if (mListenner != null) {
                                mListenner.OnFailure(e);
                            }
                        }
                    });
                }
            }
        }.start();
    }

    public void SendMsg(final String msg) {
        new Thread() {
            @Override
            public void run() {
                try {
                    BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(os));
                    bw.write(msg);
                    bw.newLine();
                    bw.flush();
                } catch (IOException e) {
                    mListenner.OnFailure(e);
                }

            }
        }.start();

    }

    public void onTcpDestroy() throws IOException {
        if (is != null){
            is.close();
        }

        if (os != null){
            os.close();
        }

        if (mSocket != null) {
            mSocket.close();
        }
    }

    public interface OnMsgReturnedListenner {
        void OnMsgReturned(String msg);

        void OnFailure(Exception e);
    }

    public void setOnMsgReturnedListenner(OnMsgReturnedListenner listenner) {
        mListenner = listenner;
    }

    public void readServerMsg() throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(is));
        String line = null;
        while ((line = br.readLine()) != null) {
            final String finalLine = line;
            handler.post(new Runnable() {
                @Override
                public void run() {
                    if (mListenner != null) {
                        mListenner.OnMsgReturned(finalLine);
                    }
                }
            });
        }
    }


}
