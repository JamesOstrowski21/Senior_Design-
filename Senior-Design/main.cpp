#include "mainwindow.h"

#include <QApplication>

#include <QFile>


int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    //Set style sheet
    QFile styleSheet("E:/Senior-Design/Senior_Design-/Senior-Design/Darkeum/Darkeum.qss");
    styleSheet.open(QFile::ReadOnly);
    QString style = QLatin1String(styleSheet.readAll());
    a.setStyleSheet(style);
    MainWindow w;
    w.show();
    return a.exec();
}
