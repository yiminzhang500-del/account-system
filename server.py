package com.company.accountapp;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.os.Bundle;
import android.os.Environment;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;

public class HomeActivity extends AppCompatActivity {

    TextView tvWelcome, tvIncome, tvPay, tvMoney;
    TextView tvMonthIncome, tvMonthPay, tvMonthMoney;

    Button btnAdd, btnList, btnRequest, btnLogout, btnChart, btnExcel;

    DBHelper helper;
    String username = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);

        tvWelcome = findViewById(R.id.tvWelcome);
        tvIncome = findViewById(R.id.tvIncome);
        tvPay = findViewById(R.id.tvPay);
        tvMoney = findViewById(R.id.tvMoney);

        tvMonthIncome = findViewById(R.id.tvMonthIncome);
        tvMonthPay = findViewById(R.id.tvMonthPay);
        tvMonthMoney = findViewById(R.id.tvMonthMoney);

        btnAdd = findViewById(R.id.btnAdd);
        btnList = findViewById(R.id.btnList);
        btnRequest = findViewById(R.id.btnRequest);
        btnLogout = findViewById(R.id.btnLogout);
        btnChart = findViewById(R.id.btnChart);
        btnExcel = findViewById(R.id.btnExcel);

        helper = new DBHelper(this);

        username = getIntent().getStringExtra("username");
        if (username == null) username = "";

        tvWelcome.setText("欢迎你，" + username);

        loadData();

        btnAdd.setOnClickListener(v ->
                startActivity(new Intent(this, AddRecordActivity.class)));

        btnList.setOnClickListener(v ->
                startActivity(new Intent(this, RecordListActivity.class)));

        btnRequest.setOnClickListener(v ->
                startActivity(new Intent(this, RequestMoneyActivity.class)));

        btnChart.setOnClickListener(v ->
                startActivity(new Intent(this, ChartActivity.class)));

        btnExcel.setOnClickListener(v ->
                exportCSV());

        btnLogout.setOnClickListener(v -> finish());
    }

    @Override
    protected void onResume() {
        super.onResume();
        loadData();
    }

    private void loadData() {

        double income = 0;
        double pay = 0;
        double monthIncome = 0;
        double monthPay = 0;

        String month =
                new java.text.SimpleDateFormat("yyyy-MM")
                        .format(new java.util.Date());

        SQLiteDatabase db =
                helper.getReadableDatabase();

        Cursor c = db.rawQuery(
                "select type,money,remark,date,currency from records",
                null
        );

        while (c.moveToNext()) {

            String type = c.getString(0);
            String moneyStr = c.getString(1);
            String date = c.getString(3);

            double money = 0;

            try {
                money = Double.parseDouble(moneyStr);
            } catch (Exception e) {
                money = 0;
            }

            if ("收入".equals(type)) {
                income += money;
            } else {
                pay += money;
            }

            if (date != null && date.startsWith(month)) {

                if ("收入".equals(type)) {
                    monthIncome += money;
                } else {
                    monthPay += money;
                }
            }
        }

        c.close();

        tvIncome.setText("总收入：" + income);
        tvPay.setText("总支出：" + pay);
        tvMoney.setText("当前余额：" + (income - pay));

        tvMonthIncome.setText("本月收入：" + monthIncome);
        tvMonthPay.setText("本月支出：" + monthPay);
        tvMonthMoney.setText("本月结余：" + (monthIncome - monthPay));
    }

    // 导出到 Download 文件夹
    private void exportCSV() {

        try {

            SQLiteDatabase db =
                    helper.getReadableDatabase();

            Cursor c = db.rawQuery(
                    "select type,money,remark,date,currency from records",
                    null
            );

            File dir =
                    Environment.getExternalStoragePublicDirectory(
                            Environment.DIRECTORY_DOWNLOADS
                    );

            if (dir != null && !dir.exists()) {
                dir.mkdirs();
            }

            File file =
                    new File(dir, "AccountReport.csv");

            FileOutputStream fos =
                    new FileOutputStream(file);

            // 防止Excel中文乱码
            fos.write(0xEF);
            fos.write(0xBB);
            fos.write(0xBF);

            String title =
                    "类型,金额,备注,日期,货币单位\r\n";

            fos.write(title.getBytes("UTF-8"));

            while (c.moveToNext()) {

                String type = c.getString(0);
                String money = c.getString(1);
                String remark = c.getString(2);
                String date = c.getString(3);
                String currency = c.getString(4);

                if (remark == null) remark = "";
                remark = remark.replace(",", "，");

                String line =
                        type + "," +
                        money + "," +
                        remark + "," +
                        date + "," +
                        currency +
                        "\r\n";

                fos.write(line.getBytes("UTF-8"));
            }

            c.close();
            fos.flush();
            fos.close();

            Toast.makeText(
                    this,
                    "导出成功：Download/AccountReport.csv",
                    Toast.LENGTH_LONG
            ).show();

        } catch (Exception e) {

            e.printStackTrace();

            Toast.makeText(
                    this,
                    "导出失败",
                    Toast.LENGTH_LONG
            ).show();
        }
    }
}
