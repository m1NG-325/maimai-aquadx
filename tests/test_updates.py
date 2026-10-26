import httpx
import pytest

from app.updates import check_latest, UpdateCheckError, RELEASES_URL


@pytest.mark.parametrize('tag,state', [('v2.2','newer'),('v2.10','newer'),('v2.1.0','current'),('v2.0','ahead')])
def test_release_version_comparison(tag, state):
    def respond(request):
        assert request.url.host == 'api.github.com'
        assert 'authorization' not in request.headers
        return httpx.Response(200, json={'tag_name':tag,'body':'更新说明','draft':False,'prerelease':False})
    result=check_latest('2.1',transport=httpx.MockTransport(respond))
    assert result['state']==state
    assert result['notes']=='更新说明'
    assert result['url']==RELEASES_URL+'/tag/'+tag


@pytest.mark.parametrize('payload', [[], {'tag_name':'latest'}, {'tag_name':'v2.2-rc1'}, {'tag_name':'v2.2','draft':True}, {'tag_name':'v2.2','prerelease':True}])
def test_invalid_release_is_not_reported_as_update(payload):
    with pytest.raises(UpdateCheckError):
        check_latest('2.1',transport=httpx.MockTransport(lambda _:httpx.Response(200,json=payload)))


@pytest.mark.parametrize('status,fragment', [(403,'限制'),(429,'限制'),(404,'正式版本'),(500,'无法连接')])
def test_http_errors_are_actionable(status,fragment):
    with pytest.raises(UpdateCheckError,match=fragment):
        check_latest('2.1',transport=httpx.MockTransport(lambda _:httpx.Response(status)))


def test_timeout_is_not_reported_as_up_to_date():
    def timeout(request):
        raise httpx.ReadTimeout('timeout',request=request)
    with pytest.raises(UpdateCheckError,match='网络'):
        check_latest('2.1',transport=httpx.MockTransport(timeout))


def test_release_body_and_links_are_not_executed(monkeypatch):
    monkeypatch.setenv('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtWidgets import QApplication,QTextBrowser,QPushButton
    from app.desktop_dialogs import NoticeDialog,UpdateDialog
    app=QApplication.instance() or QApplication([])
    dialog=NoticeDialog();dialog.show();app.processEvents()
    button=dialog.findChild(QPushButton,'noticeConfirm');button.click()
    assert dialog.result()==dialog.DialogCode.Accepted
    dialog=UpdateDialog({'current':'2.1','latest':'v2.2','state':'newer','notes':'<img src="https://example.com/tracker">','url':RELEASES_URL})
    assert dialog.findChild(QTextBrowser).toPlainText().startswith('<img')
    dialog.close()


def test_help_and_async_check_recover_after_success_and_failure(tmp_path,monkeypatch):
    monkeypatch.setenv('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtWidgets import QApplication,QLabel,QMessageBox
    from PySide6.QtTest import QTest
    from app.desktop_core import DesktopCore
    from app.desktop_ui import MainWindow
    from app.desktop_dialogs import UpdateDialog
    import app.updates as updates
    app=QApplication.instance() or QApplication([])
    core=DesktopCore(tmp_path/'profile',settings_path=tmp_path/'settings.json')
    window=MainWindow(core)
    labels=window.pages.widget(12).findChildren(QLabel)
    assert any(updates.REPOSITORY_URL in label.text() and label.openExternalLinks() for label in labels)
    shown=[]
    monkeypatch.setattr(UpdateDialog,'exec',lambda self:shown.append(self.windowTitle()))
    monkeypatch.setattr(QMessageBox,'exec',lambda self:shown.append(self.windowTitle()))
    def wait_for_worker():
        for _ in range(200):
            app.processEvents()
            if not window.workers:break
            QTest.qWait(10)
        assert not window.workers
        assert window.update_button.isEnabled() and window.update_button.text()=='检查更新'
    monkeypatch.setattr(updates,'check_latest',lambda _:dict(current='2.1',latest='v2.2',state='newer',url=RELEASES_URL,notes='新增功能'))
    window.check_updates();assert not window.update_button.isEnabled();wait_for_worker()
    def fail(_):raise UpdateCheckError('无法连接 GitHub')
    monkeypatch.setattr(updates,'check_latest',fail)
    window.check_updates();wait_for_worker()
    assert shown==['检查更新','检查更新失败']
    window.close()
