/********************************************************************************
** Form generated from reading UI file 'mainwindow.ui'
**
** Created by: Qt User Interface Compiler version 6.6.2
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINWINDOW_H
#define UI_MAINWINDOW_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QFrame>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QTabWidget>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QWidget *centralwidget;
    QVBoxLayout *verticalLayout_2;
    QVBoxLayout *verticalLayout;
    QFrame *application_header;
    QHBoxLayout *horizontalLayout_2;
    QLabel *application_title;
    QWidget *internet_widget;
    QGridLayout *gridLayout;
    QLabel *internet_text;
    QTabWidget *tabWidget;
    QWidget *decode_page;
    QWidget *location_page;
    QWidget *automation_page;
    QMenuBar *menubar;
    QStatusBar *statusbar;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName("MainWindow");
        MainWindow->resize(824, 611);
        centralwidget = new QWidget(MainWindow);
        centralwidget->setObjectName("centralwidget");
        verticalLayout_2 = new QVBoxLayout(centralwidget);
        verticalLayout_2->setObjectName("verticalLayout_2");
        verticalLayout = new QVBoxLayout();
        verticalLayout->setObjectName("verticalLayout");
        application_header = new QFrame(centralwidget);
        application_header->setObjectName("application_header");
        application_header->setMinimumSize(QSize(800, 60));
        application_header->setFrameShape(QFrame::StyledPanel);
        application_header->setFrameShadow(QFrame::Raised);
        horizontalLayout_2 = new QHBoxLayout(application_header);
        horizontalLayout_2->setObjectName("horizontalLayout_2");
        application_title = new QLabel(application_header);
        application_title->setObjectName("application_title");
        application_title->setMinimumSize(QSize(600, 40));

        horizontalLayout_2->addWidget(application_title, 0, Qt::AlignLeft|Qt::AlignVCenter);

        internet_widget = new QWidget(application_header);
        internet_widget->setObjectName("internet_widget");
        internet_widget->setMinimumSize(QSize(60, 35));
        internet_widget->setMaximumSize(QSize(200, 40));
        gridLayout = new QGridLayout(internet_widget);
        gridLayout->setObjectName("gridLayout");
        internet_text = new QLabel(internet_widget);
        internet_text->setObjectName("internet_text");
        internet_text->setMaximumSize(QSize(110, 50));

        gridLayout->addWidget(internet_text, 0, 0, 1, 1);


        horizontalLayout_2->addWidget(internet_widget, 0, Qt::AlignHCenter);


        verticalLayout->addWidget(application_header);

        tabWidget = new QTabWidget(centralwidget);
        tabWidget->setObjectName("tabWidget");
        tabWidget->setMinimumSize(QSize(800, 60));
        decode_page = new QWidget();
        decode_page->setObjectName("decode_page");
        tabWidget->addTab(decode_page, QString());
        location_page = new QWidget();
        location_page->setObjectName("location_page");
        tabWidget->addTab(location_page, QString());
        automation_page = new QWidget();
        automation_page->setObjectName("automation_page");
        tabWidget->addTab(automation_page, QString());

        verticalLayout->addWidget(tabWidget);


        verticalLayout_2->addLayout(verticalLayout);

        MainWindow->setCentralWidget(centralwidget);
        menubar = new QMenuBar(MainWindow);
        menubar->setObjectName("menubar");
        menubar->setGeometry(QRect(0, 0, 824, 22));
        MainWindow->setMenuBar(menubar);
        statusbar = new QStatusBar(MainWindow);
        statusbar->setObjectName("statusbar");
        MainWindow->setStatusBar(statusbar);

        retranslateUi(MainWindow);

        tabWidget->setCurrentIndex(0);


        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QCoreApplication::translate("MainWindow", "MainWindow", nullptr));
        application_title->setText(QCoreApplication::translate("MainWindow", "InteliTrack", nullptr));
#if QT_CONFIG(tooltip)
        internet_widget->setToolTip(QString());
#endif // QT_CONFIG(tooltip)
        internet_text->setText(QCoreApplication::translate("MainWindow", "Internet Connection", nullptr));
        tabWidget->setTabText(tabWidget->indexOf(decode_page), QCoreApplication::translate("MainWindow", "Decode", nullptr));
        tabWidget->setTabText(tabWidget->indexOf(location_page), QCoreApplication::translate("MainWindow", "Location", nullptr));
        tabWidget->setTabText(tabWidget->indexOf(automation_page), QCoreApplication::translate("MainWindow", "Automation/Scheduling", nullptr));
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINWINDOW_H
