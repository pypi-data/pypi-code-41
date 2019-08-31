

def False_pred_imgs(X, y, y_pred, label_encodings_dict = None):
    False_preds_mask = (y!=y_pred).any(axis=1)

    X_False_preds = X[False_preds_mask==True]
    y_true_False_preds = y[False_preds_mask==True]
    y_pred_False_preds = y_pred[False_preds_mask==True]

    n_columns = 3
    fig, ax_list = plt.subplots(1,n_columns)
    p=0
    for i in range(X_False_preds.shape[0]):
        True_label = y_true_False_preds[i,:]
        pred_label = y_pred_False_preds[i,:]

        if label_encodings_dict != None:
            True_label = [key for key in label_encodings_dict.keys() if [label_encodings_dict[key]]== True_label]
            pred_label = [key for key in label_encodings_dict.keys() if [label_encodings_dict[key]]== pred_label]
        title = 'True_label:'+str(True_label) + '\n' + \
                'pred_label:'+ str(pred_label) +'\n'

        if p > n_columns-1:
            fig.tight_layout(rect=(0,0,n_columns, 1))
            plt.show()

            p=0
            fig, ax_list = plt.subplots(1,n_columns)
            for ax in ax_list:
                ax.imshow(np.ones((256,256,3)))
                ax.grid(which='both',visible=False)
                ax.axis('off')

        ax_list[p].set_title(title)
        ax_list[p].imshow(X_False_preds[i,:,:,:])
        ax_list[p].axis('off')
        ax_list[p].grid(which='both',visible=False)

        p+=1
    