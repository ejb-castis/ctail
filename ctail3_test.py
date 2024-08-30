import pytest

from ctail3 import (
    Options,
    format_cilog,
    format_lgufastlog,
    format_ncsacombinedlog,
    format_simple_log4j,
    format_simple_trace
    )


@pytest.fixture
def setup():
    # 이 부분에 테스트 전에 실행되어야 하는 코드를 작성합니다.
    print("Setting up and Go")
    print("=====================================")


def test_format_lgufastlog(setup):    
    options = Options()
    options.skip_date = False
    options.skip_time = False

    log = "SSAIScheduler,1.0.64,,2024-08-29,00:00:00.000,INFO,ScheduleManagerScheduler(198),,\"CheckCdpChannel - start\""
    formatted_log, error, msg = format_lgufastlog(log, options)
    print(formatted_log, error, msg)


    log = "SSAIScheduler,1.0.64,thekids_test_20240520,2024-08-29,00:00:00.000,INFO,WorkerTask(66),,\"Stop to send adSchedule, channel : thekids_test_20240520\""
    formatted_log, error, msg = format_lgufastlog(log, options)
    print(formatted_log, error, msg)

    # assert error == False
    # assert "127.0.0.1" in formatted_log
    # assert "200" in formatted_log
    # assert "/index.html" in formatted_log
    

def test_format_ncsacombinedlog(setup):
    options = Options()
    options.skip_date = False
    options.skip_time = False

    log = "127.0.0.1 - - [01/Jan/2000:00:00:00 +0000] \"GET /index.html HTTP/1.1\" 200 2326 \"-\" \"Mozilla/5.0\""
    formatted_log, error, msg = format_ncsacombinedlog(log, options)
    print(formatted_log, error, msg)

    assert error == False
    assert "127.0.0.1" in formatted_log
    assert "200" in formatted_log
    assert "/index.html" in formatted_log

    log = "127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] \"GET /apache_pb.gif HTTP/1.0\" 200 2326 \"http://www.example.com/start.html\" \"Mozilla/4.08 [en] (Win98; I ;Nav)\""
    formatted_log, error, msg = format_ncsacombinedlog(log, options)
    print(formatted_log, error, msg)
    assert error == False

    log = "2024-05-15 20:01:55,[INFO ],AbstractHandlerMethodMapping.java,register(543):\"Mapped \"{[/admin/getTransferApprovalRequestStatusHistoryList],methods=[POST]}\" onto public cbank.util.DataTableObject cbank.controller.AdminController.getTransferApprovalRequestStatusHistoryList(org.springframework.ui.Model,javax.servlet.http.HttpServletRequest,java.lang.String,java.lang.String,int,int,int) throws java.lang.Exception\""
    formatted_log, error, msg = format_ncsacombinedlog(log, options)
    print(formatted_log, error, msg)


def test_format_ncsacombinedlog_with_invalid_log(setup):
    options = Options()
    options.skip_date = False
    options.skip_time = False

    log = "invalid log"
    formatted_log, error, msg = format_ncsacombinedlog(log, options)
    assert error == True
    assert formatted_log == "invalid log"

def test_format_simple_log4j(setup):
    options = Options()
    options.skip_date = False
    options.skip_time = False

    log = "2024-05-15 20:01:55,[INFO ],AbstractHandlerMethodMapping.java,register(543):\"Mapped \"{[/admin/getTransferApprovalRequestStatusHistoryList],methods=[POST]}\" onto public cbank.util.DataTableObject cbank.controller.AdminController.getTransferApprovalRequestStatusHistoryList(org.springframework.ui.Model,javax.servlet.http.HttpServletRequest,java.lang.String,java.lang.String,int,int,int) throws java.lang.Exception\""
    formatted_log, error, msg = format_simple_log4j(log, options)
    print(formatted_log, error)

    log = "2024-05-15 20:01:53,[INFO ],LogHelper.java                ,logPersistenceUnitInformation(46):\"HHH000204: Processing PersistenceUnitInfo [\nname: cbank\n...\""
    formatted_log, error, msg = format_simple_log4j(log, options)
    print(formatted_log, error, msg)

def test_format_simple_trace(setup):
    options = Options()
    options.skip_date = False
    options.skip_time = False

    java_trace = """
    java.lang.NullPointerException
	at cbank.controller.BillController.getMakeBillView(BillController.java:103)
	at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
	at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
	at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
	at java.lang.reflect.Method.invoke(Method.java:498)
	at org.springframework.web.method.support.InvocableHandlerMethod.doInvoke(InvocableHandlerMethod.java:205)
	at org.springframework.web.method.support.InvocableHandlerMethod.invokeForRequest(InvocableHandlerMethod.java:133)
    """
    formatted_log, error, msg = format_simple_trace(java_trace, options)
    print(formatted_log, error, msg)
